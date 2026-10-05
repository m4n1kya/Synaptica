# Backend API

Synaptica's backend is a high-performance FastAPI service designed for asynchronous extraction of knowledge graphs from complex PDFs.

## Stack
- **FastAPI**: Async HTTP handling and routing
- **Uvicorn**: ASGI web server
- **PyMuPDF**: PDF text extraction
- **Google Gemini 3.6 Flash**: LLM for structured fact extraction
- **Firebase Firestore**: Persistent storage for extracted knowledge bases

## Rate Limiting
To comply with Gemini's free-tier rate limits, chunks are processed in smaller batches (max 6) sequentially rather than concurrently. This prevents `429 RESOURCE_EXHAUSTED` and `503 UNAVAILABLE` errors on large PDFs.
