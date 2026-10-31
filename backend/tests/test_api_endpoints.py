"""
Integration contract tests for Synaptica REST API endpoints.
"""
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


