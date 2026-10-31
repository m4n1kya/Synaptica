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
├── requirements.txt     # Pinned production dependencies
└── tests/               # Comprehensive automated test suite (50+ unit & contract tests)
    ├── test_api_endpoints.py    # REST API contracts, status codes, query filtering & error handling
    ├── test_demo_data.py        # Dataset referential integrity and case study constraints
    ├── test_fact_extractor.py   # JSON repair, code fence stripping, and safety fallbacks
    ├── test_fact_linker.py      # Candidate pair generation and incremental linking logic
    ├── test_firestore_store.py  # Mocked Firestore CRUD and cascade deletions
    ├── test_knowledge_store.py  # In-memory store lifecycle, search, and graph querying
    ├── test_models.py           # Pydantic v2 validation and confidence boundary checks
    └── test_pdf_processor.py    # Sliding-window page chunker and table detection heuristics
```

## Running Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Running Tests & Coverage

```bash
pytest backend/tests -v --cov=backend --cov-report=term-missing
```

Interactive OpenAPI documentation is automatically served at `http://localhost:8000/docs`.
