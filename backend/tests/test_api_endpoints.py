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
