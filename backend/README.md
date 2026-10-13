# Synaptica — Backend Service

Asynchronous **FastAPI** service powering PDF ingestion, LLM-driven atomic fact extraction, cross-document relationship reconciliation, and multi-tenant persistence.

## Module Structure

```text
backend/
├── main.py              # FastAPI application, CORS, auth middleware, REST endpoints
├── models.py            # Pydantic v2 schemas (Document, Fact, Context, Relationship, CaseStudy)
├── pdf_processor.py     # Multi-page PDF parsing and overlapping sliding-window chunker
├── fact_extractor.py    # Gemini AI extraction pipeline with exponential backoff & JSON recovery
├── fact_linker.py       # Pairwise candidate filtering and LLM relationship classification
├── firestore_store.py   # Multi-tenant Google Cloud Firestore persistence layer
├── knowledge_store.py   # In-memory store for fallback & static dataset generation
├── demo_data.py         # Pre-verified macroeconomic & corporate financial datasets
└── requirements.txt     # Pinned production dependencies
```

## Running Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Interactive OpenAPI documentation is automatically served at `http://localhost:8000/docs`.
