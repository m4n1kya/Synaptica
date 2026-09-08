"""
Synaptica - Main API Server
FastAPI application serving the knowledge layer API and frontend static files.
"""
import os
import sys
import uuid
import shutil
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth
import uvicorn

# Add backend dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import extract_pdf_text, chunk_pages
from fact_extractor import extract_all_facts
from fact_linker import link_all_facts
from firestore_store import FirestoreStore

# -- App Setup --------------------------------------------------------------

app = FastAPI(
    title="Synaptica API",
    description="AI-Powered Fact Knowledge Layer - Extract, Link, and Reconcile facts across documents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -- Authentication ---------------------------------------------------------

security = HTTPBearer(auto_error=False)

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        return None
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        print("Token verification failed:", e)
        return None

def require_user(user_id: Optional[str] = Depends(get_current_user)):
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id

# -- Health & Stats ---------------------------------------------------------

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "synaptica", "version": "1.0.0"}

@app.get("/api/stats")
async def get_stats(user_id: Optional[str] = Depends(get_current_user)):
    if not user_id:
        return {"documents": 0, "facts": 0, "relationships": 0, "cases": 0}
    store = FirestoreStore(user_id)
    return {
        "documents": len(store.get_all_documents()),
        "facts": len(store.get_all_facts()),
        "relationships": len(store.get_relationships()),
        "cases": 0
    }

# -- Documents --------------------------------------------------------------

@app.get("/api/documents")
async def list_documents(user_id: str = Depends(require_user)):
    store = FirestoreStore(user_id)
    docs = store.get_all_documents()
    return [d.model_dump() for d in docs]


@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str, user_id: str = Depends(require_user)):
    store = FirestoreStore(user_id)
    doc_ref = store.user_ref.collection('documents').document(doc_id).get()
    if not doc_ref.exists:
        raise HTTPException(status_code=404, detail="Document not found")
    
    facts = store.get_all_facts(doc_id=doc_id)
    return {
        "document": doc_ref.to_dict(),
        "facts": [f.model_dump() for f in facts]
    }


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str, user_id: str = Depends(require_user)):
    store = FirestoreStore(user_id)
    success = store.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success", "message": "Document deleted"}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...), user_id: Optional[str] = Depends(get_current_user)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    doc_id = f"doc-{uuid.uuid4().hex[:8]}"
    filepath = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")
    
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    from models import Document
    doc = Document(
        id=doc_id,
        filename=file.filename,
        original_filename=file.filename,
        status="parsing",
        dataset="uploaded"
    )

    doc_content = extract_pdf_text(filepath)
    if not doc_content:
        doc.status = "error"
        return JSONResponse(status_code=500, content={"error": "Failed to extract text", "doc_id": doc_id})

    doc.page_count = doc_content.total_pages
    doc.status = "extracting"

    api_key = os.environ.get("GEMINI_API_KEY", "")
    facts = []
    new_rels = []
    
    if api_key:
        chunks = chunk_pages(doc_content)
        facts = await extract_all_facts(chunks, doc_id, file.filename, api_key)
        
        if user_id:
            store = FirestoreStore(user_id)
            existing_facts = [f for f in store.get_all_facts() if f.source_doc_id != doc_id]
            if existing_facts and facts:
                from fact_linker import link_incremental
                new_rels = await link_incremental(facts, existing_facts, api_key)
                
    doc.fact_count = len(facts)
    doc.status = "processed"

    if user_id:
        store = FirestoreStore(user_id)
        store.add_document(doc)
        for fact in facts:
            store.add_fact(fact)
        for rel in new_rels:
            store.add_relationship(rel)

    return {
        "doc_id": doc_id,
        "document": doc.model_dump(),
        "facts": [f.model_dump() for f in facts],
        "relationships": [r.model_dump() for r in new_rels],
        "status": doc.status,
        "message": "Processed successfully"
    }

# -- Facts ------------------------------------------------------------------

@app.get("/api/facts")
async def list_facts(
    category: Optional[str] = Query(None),
    doc_id: Optional[str] = Query(None),
    min_confidence: float = Query(0.0),
    user_id: str = Depends(require_user)
):
    store = FirestoreStore(user_id)
    facts = store.get_all_facts(category=category, doc_id=doc_id, min_confidence=min_confidence)
    return [f.model_dump() for f in facts]

@app.get("/api/categories")
async def list_categories(user_id: str = Depends(require_user)):
    store = FirestoreStore(user_id)
    facts = store.get_all_facts()
    categories = {}
    for f in facts:
        categories[f.category] = categories.get(f.category, 0) + 1
    return [{"name": k, "count": v} for k, v in sorted(categories.items(), key=lambda x: -x[1])]

# -- Relationships ----------------------------------------------------------

@app.get("/api/relationships")
async def list_relationships(user_id: str = Depends(require_user)):
    store = FirestoreStore(user_id)
    rels = store.get_relationships()
    facts = {f.id: f for f in store.get_all_facts()}
    
    enriched = []
    for rel in rels:
        fact_a = facts.get(rel.fact_a_id)
        fact_b = facts.get(rel.fact_b_id)
        enriched.append({
            "relationship": rel.model_dump(),
            "fact_a": fact_a.model_dump() if fact_a else None,
            "fact_b": fact_b.model_dump() if fact_b else None,
        })
    return enriched

@app.get("/api/cases")
async def get_cases(user_id: str = Depends(require_user)):
    return []

# -- Static Frontend -------------------------------------------------------

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

@app.get("/")
async def serve_root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Synaptica API is running."}

if os.path.exists(FRONTEND_DIR):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
    assets_dir = os.path.join(FRONTEND_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
