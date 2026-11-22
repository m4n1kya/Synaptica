"""
Integration contract tests for Synaptica REST API endpoints.
"""
from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify that /api/health responds with 200 OK and valid status payload."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    assert data.get("service") == "synaptica"
    assert "version" in data


def test_readiness_endpoint():
    """Verify /api/ready reports ready status and loaded entity counts."""
    response = client.get("/api/ready")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ready"
    assert data.get("service") == "synaptica"
    assert data.get("documents_loaded") > 0
    assert data.get("facts_loaded") > 0
    assert data.get("relationships_loaded") > 0
    assert data.get("cases_loaded") > 0


def test_stats_endpoint():
    """Verify /api/stats returns aggregated metrics across the knowledge layer."""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "total_facts" in data
    assert "total_relationships" in data
    assert "avg_confidence" in data
    assert data["total_documents"] >= 0


def test_documents_endpoint():
    """Verify /api/documents returns an array of ingested document summaries."""
    response = client.get("/api/documents")
    assert response.status_code == 200
    docs = response.json()
    assert isinstance(docs, list)
    if docs:
        first = docs[0]
        assert "id" in first
        assert "filename" in first
        assert "page_count" in first


def test_documents_endpoint_dataset_filtering():
    """Verify /api/documents supports filtering by dataset query parameter."""
    res_macro = client.get("/api/documents?dataset=india-macroeconomy")
    assert res_macro.status_code == 200
    macro_docs = res_macro.json()
    assert len(macro_docs) > 0
    for doc in macro_docs:
        assert doc["dataset"] == "india-macroeconomy"

    res_nonexistent = client.get("/api/documents?dataset=non_existent_dataset_abc")
    assert res_nonexistent.status_code == 200
    assert res_nonexistent.json() == []


def test_cases_endpoint():
    """Verify /api/cases serves the analytical case studies."""
    response = client.get("/api/cases")
    assert response.status_code == 200
    cases = response.json()
    assert isinstance(cases, list)
    assert len(cases) == 4
    case_types = [c.get("case_type") for c in cases]
    assert "corroboration" in case_types
    assert "contradiction" in case_types


def test_facts_filtering_endpoint():
    """Verify /api/facts query endpoint responds with fact list."""
    response = client.get("/api/facts")
    assert response.status_code == 200
    facts = response.json()
    assert isinstance(facts, list)


def test_relationships_endpoint():
    """Verify /api/relationships responds with graph edges."""
    response = client.get("/api/relationships")
    assert response.status_code == 200
    rels = response.json()
    assert isinstance(rels, list)


def test_categories_endpoint():
    """Verify /api/categories returns category names and fact distribution counts."""
    response = client.get("/api/categories")
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)
    assert len(categories) > 0
    first = categories[0]
    assert "name" in first
    assert "count" in first
    assert first["count"] >= 1


def test_get_document_detail_success():
    """Verify /api/documents/{doc_id} retrieves document metadata and extracted facts."""
    response = client.get("/api/documents/doc-eco-survey")
    assert response.status_code == 200
    data = response.json()
    assert "document" in data
    assert "facts" in data
    assert data["document"]["id"] == "doc-eco-survey"
    assert isinstance(data["facts"], list)
    assert len(data["facts"]) > 0


def test_get_document_detail_not_found():
    """Verify /api/documents/{doc_id} returns 404 for an invalid doc_id."""
    response = client.get("/api/documents/non_existent_doc_12345")
    assert response.status_code == 404
    data = response.json()
    assert data.get("detail") == "Document not found"


def test_delete_document_unauthorized():
    """Verify /api/documents/{doc_id} rejects deletion when unauthenticated."""
    response = client.delete("/api/documents/doc-eco-survey")
    assert response.status_code == 401
    assert "Authentication required" in response.json().get("detail", "")


def test_upload_invalid_file_extension():
    """Verify /api/upload rejects non-PDF file uploads with 400 Bad Request."""
    files = {"file": ("notes.txt", b"plain text content", "text/plain")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 400
    assert "Only PDF files are accepted" in response.json().get("detail", "")


def test_facts_pagination_limit_and_offset():
    """Verify /api/facts respects limit and offset query parameters."""
    res_all = client.get("/api/facts")
    assert res_all.status_code == 200
    all_facts = res_all.json()
    assert len(all_facts) >= 5

    res_limited = client.get("/api/facts?limit=3")
    assert res_limited.status_code == 200
    limited_facts = res_limited.json()
    assert len(limited_facts) == 3
    assert limited_facts == all_facts[:3]

    res_offset = client.get("/api/facts?limit=2&offset=2")
    assert res_offset.status_code == 200
    offset_facts = res_offset.json()
    assert len(offset_facts) == 2
    assert offset_facts == all_facts[2:4]


def test_facts_text_search():
    """Verify /api/facts performs case-insensitive text search across statements."""
    response = client.get("/api/facts?search=gdp")
    assert response.status_code == 200
    matching_facts = response.json()
    assert len(matching_facts) > 0
    for fact in matching_facts:
        searchable = f"{fact['statement']} {fact['evidence_text']}".lower()
        assert "gdp" in searchable


def test_relationships_filtered_by_type():
    """Verify /api/relationships filters by relationship_type."""
    res_corroborates = client.get("/api/relationships?relationship_type=corroborates")
    assert res_corroborates.status_code == 200
    corroborates = res_corroborates.json()
    assert len(corroborates) > 0
    for item in corroborates:
        assert item["relationship"]["relationship_type"] == "corroborates"


def test_get_fact_detail_success():
    """Verify /api/facts/{fact_id} retrieves a specific fact with its linked relationships."""
    res_facts = client.get("/api/facts?limit=1")
    assert res_facts.status_code == 200
    first_fact = res_facts.json()[0]
    fact_id = first_fact["id"]

    response = client.get(f"/api/facts/{fact_id}")
    assert response.status_code == 200
    data = response.json()
    assert "fact" in data
    assert data["fact"]["id"] == fact_id
    assert "related" in data
    assert isinstance(data["related"], list)


def test_get_fact_detail_not_found():
    """Verify /api/facts/{fact_id} returns 404 for non-existent fact ID."""
    response = client.get("/api/facts/fact-nonexistent-999")
    assert response.status_code == 404
    assert response.json().get("detail") == "Fact not found"


def test_debug_env_endpoint():
    """Verify /api/debug/env reports masked presence of core environment variables."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "AIzaSySecret", "FIREBASE_SERVICE_ACCOUNT": "{}"}):
        response = client.get("/api/debug/env")
        assert response.status_code == 200
        data = response.json()
        assert data["GEMINI_API_KEY"] == "SET"
        assert data["FIREBASE_SERVICE_ACCOUNT"] == "SET"


def test_debug_gemini_missing_key():
    """Verify /api/debug/gemini returns error when GEMINI_API_KEY is unset."""
    with patch.dict("os.environ", {}, clear=True):
        response = client.get("/api/debug/gemini")
        assert response.status_code == 200
        assert response.json().get("error") == "GEMINI_API_KEY not set"


def test_debug_gemini_success_mock():
    """Verify /api/debug/gemini generates response payload successfully."""
    mock_resp = MagicMock()
    mock_resp.text = '[{"statement": "Test fact works", "category": "General", "confidence": 0.9}]'

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)

    with patch.dict("os.environ", {"GEMINI_API_KEY": "dummy_key"}), patch("google.genai.Client", return_value=mock_client):
        response = client.get("/api/debug/gemini")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "Test fact works" in data["raw_text"]


def test_invalid_bearer_token_fallback():
    """Verify invalid Authorization header logs warning and falls back to demo mode without 500 error."""
    with patch("firebase_admin.auth.verify_id_token", side_effect=Exception("Invalid token")):
        response = client.get("/api/stats", headers={"Authorization": "Bearer fake_token_xyz"})
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "total_facts" in data


def test_serve_root_endpoint():
    """Verify GET / returns index.html shell or fallback message."""
    response = client.get("/")
    assert response.status_code == 200


def test_upload_pdf_extraction_failure():
    """Verify /api/upload returns 500 when PDF text extraction returns None."""
    with patch("main.extract_pdf_text", return_value=None):
        files = {"file": ("corrupted.pdf", b"%PDF-1.4 mock content", "application/pdf")}
        response = client.post("/api/upload", files=files)
        assert response.status_code == 500
        assert response.json().get("error") == "Failed to extract text"


def test_upload_pdf_success_mock():
    """Verify /api/upload extracts facts and returns processed document payload."""
    from pdf_processor import DocumentContent, PageContent
    from models import Fact

    mock_content = DocumentContent(
        filename="test_upload.pdf",
        total_pages=1,
        pages=[PageContent(page_number=1, text="Headline GDP grew 8.2% in FY24.")]
    )
    mock_fact = Fact(
        id="f-upload-1",
        statement="GDP grew 8.2% in FY24",
        category="Macroeconomics",
        confidence=0.95,
        source_doc_name="test_upload.pdf",
    )

    with patch("main.extract_pdf_text", return_value=mock_content), \
         patch("main.extract_all_facts", new_callable=AsyncMock, return_value=[mock_fact]), \
         patch.dict("os.environ", {"GEMINI_API_KEY": "valid_test_key"}):

        files = {"file": ("test_upload.pdf", b"%PDF-1.4 mock content", "application/pdf")}
        response = client.post("/api/upload", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "processed"
        assert data.get("fact_count") == 1
        assert len(data.get("facts", [])) == 1
        assert data["facts"][0]["statement"] == "GDP grew 8.2% in FY24"


def test_delete_document_authenticated_success_and_not_found():
    """Verify authenticated users can delete documents or receive 404 when not found."""
    with patch("firebase_admin.auth.verify_id_token", return_value={"uid": "user_auth_1"}), \
         patch("main.FirestoreStore") as MockStore:

        mock_instance = MockStore.return_value

        # Case 1: Document deleted successfully
        mock_instance.delete_document.return_value = True
        res_ok = client.delete("/api/documents/doc-valid-1", headers={"Authorization": "Bearer token1"})
        assert res_ok.status_code == 200
        assert res_ok.json().get("status") == "success"

        # Case 2: Document does not exist
        mock_instance.delete_document.return_value = False
        res_404 = client.delete("/api/documents/doc-missing-1", headers={"Authorization": "Bearer token1"})
        assert res_404.status_code == 404
        assert res_404.json().get("detail") == "Document not found"


def test_get_document_authenticated():
    """Verify retrieving document detail for authenticated user with FirestoreStore."""
    with patch("firebase_admin.auth.verify_id_token", return_value={"uid": "user_auth_2"}), \
         patch("main.FirestoreStore") as MockStore:

        mock_instance = MockStore.return_value
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.to_dict.return_value = {"id": "doc-u1", "filename": "user_doc.pdf", "page_count": 5}

        mock_instance.user_ref.collection.return_value.document.return_value.get.return_value = doc_mock
        mock_instance.get_all_facts.return_value = []

        res = client.get("/api/documents/doc-u1", headers={"Authorization": "Bearer token2"})
        assert res.status_code == 200
        data = res.json()
        assert data["document"]["id"] == "doc-u1"

        # Test document not found
        doc_mock.exists = False
        res_404 = client.get("/api/documents/doc-u1", headers={"Authorization": "Bearer token2"})
        assert res_404.status_code == 404


def test_stats_and_cases_authenticated():
    """Verify /api/stats and /api/cases return expected data when user is authenticated."""
    with patch("firebase_admin.auth.verify_id_token", return_value={"uid": "user_auth_3"}), \
         patch("main.FirestoreStore") as MockStore:

        mock_instance = MockStore.return_value
        mock_instance.get_all_documents.return_value = [MagicMock()]
        mock_instance.get_all_facts.return_value = [MagicMock(), MagicMock()]
        mock_instance.get_relationships.return_value = []

        res_stats = client.get("/api/stats", headers={"Authorization": "Bearer token3"})
        assert res_stats.status_code == 200
        stats = res_stats.json()
        assert stats["documents"] == 1
        assert stats["facts"] == 2

        res_cases = client.get("/api/cases", headers={"Authorization": "Bearer token3"})
        assert res_cases.status_code == 200
        assert res_cases.json() == []





