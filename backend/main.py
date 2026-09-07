"""
Synaptica — Main API Server
FastAPI application serving the knowledge layer API and frontend static files.
"""
import os
import sys
import uuid
import shutil
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import uvicorn

# Add backend dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge_store import KnowledgeStore
from pdf_processor import extract_pdf_text, chunk_pages
from fact_extractor import extract_all_facts
from fact_linker import link_all_facts

# ── App Setup ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="Synaptica API",
    description="AI-Powered Fact Knowledge Layer — Extract, Link, and Reconcile facts across documents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize knowledge store with demo data
store = KnowledgeStore(load_demo=True)

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── Health & Stats ─────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "synaptica", "version": "1.0.0"}


@app.get("/api/stats")
async def get_stats():
    stats = store.get_stats()
    return stats.model_dump()


# ── Documents ──────────────────────────────────────────────────────────────

@app.get("/api/documents")
async def list_documents():
    docs = store.get_all_documents()
    return [d.model_dump() for d in docs]


@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    doc = store.documents.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    facts = store.get_all_facts(doc_id=doc_id)
    return {
        "document": doc.model_dump(),
        "facts": [f.model_dump() for f in facts]
    }


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    success = store.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success", "message": "Document deleted"}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file for fact extraction."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Save the file
    doc_id = f"doc-{uuid.uuid4().hex[:8]}"
    filepath = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")
    
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    # Create document record
    from models import Document
    doc = Document(
        id=doc_id,
        filename=file.filename,
        original_filename=file.filename,
        status="parsing",
        dataset="uploaded"
    )
    store.add_document(doc)

    # Extract text
    doc_content = extract_pdf_text(filepath)
    if not doc_content:
        doc.status = "error"
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to extract text from PDF", "doc_id": doc_id}
        )

    doc.page_count = doc_content.total_pages
    doc.status = "extracting"

    # Try to extract facts with LLM
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        chunks = chunk_pages(doc_content)
        facts = await extract_all_facts(chunks, doc_id, file.filename, api_key)
        for fact in facts:
            store.add_fact(fact)
        doc.status = "processed"
    else:
        doc.status = "processed"
        # No API key — file is parsed but facts are not extracted
    
    doc.fact_count = len(store.get_all_facts(doc_id=doc_id))

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "page_count": doc.page_count,
        "fact_count": doc.fact_count,
        "status": doc.status,
        "message": "Document processed successfully" + (
            " (fact extraction skipped — no GEMINI_API_KEY)" if not api_key else ""
        )
    }


# ── Facts ──────────────────────────────────────────────────────────────────

@app.get("/api/facts")
async def list_facts(
    category: Optional[str] = Query(None, description="Filter by category"),
    doc_id: Optional[str] = Query(None, description="Filter by document ID"),
    min_confidence: float = Query(0.0, description="Minimum confidence threshold"),
    dataset: Optional[str] = Query(None, description="Filter by dataset (india-macroeconomy / delhivery)")
):
    facts = store.get_all_facts(category=category, doc_id=doc_id, min_confidence=min_confidence)
    if dataset:
        doc_ids = [d.id for d in store.documents.values() if d.dataset == dataset]
        facts = [f for f in facts if f.source_doc_id in doc_ids]
    return [f.model_dump() for f in facts]


@app.get("/api/facts/{fact_id}")
async def get_fact(fact_id: str):
    result = store.get_fact_with_relationships(fact_id)
    if not result:
        raise HTTPException(status_code=404, detail="Fact not found")
    return {
        "fact": result["fact"].model_dump(),
        "related": [
            {
                "fact": r["fact"].model_dump(),
                "relationship": r["relationship"].model_dump()
            }
            for r in result["related"]
        ]
    }


@app.get("/api/categories")
async def list_categories():
    """Get all unique fact categories with counts."""
    categories = {}
    for f in store.facts.values():
        categories[f.category] = categories.get(f.category, 0) + 1
    return [{"name": k, "count": v} for k, v in sorted(categories.items(), key=lambda x: -x[1])]


# ── Relationships ──────────────────────────────────────────────────────────

@app.get("/api/relationships")
async def list_relationships(
    rel_type: Optional[str] = Query(None, description="Filter by type: corroborates, contradicts, contextual_difference")
):
    rels = store.get_all_relationships(rel_type=rel_type)
    # Enrich with fact data
    enriched = []
    for rel in rels:
        fact_a = store.facts.get(rel.fact_a_id)
        fact_b = store.facts.get(rel.fact_b_id)
        enriched.append({
            "relationship": rel.model_dump(),
            "fact_a": fact_a.model_dump() if fact_a else None,
            "fact_b": fact_b.model_dump() if fact_b else None,
        })
    return enriched


@app.get("/api/relationships/stats")
async def relationship_stats():
    rels = store.get_all_relationships()
    stats = {}
    for r in rels:
        stats[r.relationship_type] = stats.get(r.relationship_type, 0) + 1
    return stats


# ── Cases (The 4 Required Demonstrations) ─────────────────────────────────

@app.get("/api/cases")
async def get_cases():
    cases = store.cases
    result = []
    for case in cases:
        result.append({
            "id": case.id,
            "title": case.title,
            "case_type": case.case_type,
            "icon": case.icon,
            "summary": case.summary,
            "facts": [f.model_dump() for f in case.facts],
            "relationships": [r.model_dump() for r in case.relationships],
            "evidence_analysis": case.evidence_analysis,
            "system_reasoning": case.system_reasoning,
        })
    return result


# ── Analysis Trigger ───────────────────────────────────────────────────────

@app.post("/api/analyze")
async def analyze_documents():
    """Trigger cross-document analysis on all loaded facts."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    all_facts = store.get_all_facts()
    
    if not api_key:
        return {
            "message": "Analysis using pre-computed demo relationships (no GEMINI_API_KEY set)",
            "relationships_count": len(store.relationships)
        }

    # Run live analysis
    new_rels = await link_all_facts(all_facts, api_key)
    for rel in new_rels:
        store.add_relationship(rel)
    
    return {
        "message": f"Analysis complete. Found {len(new_rels)} new relationships.",
        "relationships_count": len(store.relationships)
    }


# ── Static Frontend ───────────────────────────────────────────────────────

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

# Serve index.html for the root
@app.get("/")
async def serve_root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Synaptica API is running. Frontend not found at " + FRONTEND_DIR}

# Mount static files (CSS, JS, assets) — must come after API routes
if os.path.exists(FRONTEND_DIR):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
    assets_dir = os.path.join(FRONTEND_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


# ── Entry Point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  [>] SYNAPTICA - AI-Powered Fact Knowledge Layer")
    print("="*60)
    print(f"  [DIR] Frontend: {FRONTEND_DIR}")
    print(f"  [DAT] Demo data: {len(store.facts)} facts, {len(store.relationships)} relationships")
    print(f"  [KEY] Gemini API: {'configured' if os.environ.get('GEMINI_API_KEY') else 'not set (demo mode)'}")
    print(f"  [WEB] Server: http://localhost:8000")
    print("="*60 + "\n")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
