"""
Unit tests for Synaptica core Pydantic data schemas.
"""
import pytest
from pydantic import ValidationError
from models import (
    Fact,
    Relationship,
    RelationshipType,
    DocumentStatus,
    Context,
    Document,
    KnowledgeLayerStats,
)


def test_relationship_type_enum():
    """Verify expected relationship types exist."""
    assert RelationshipType.CORROBORATES.value == "corroborates"
    assert RelationshipType.CONTRADICTS.value == "contradicts"
    assert RelationshipType.CONTEXTUAL_DIFFERENCE.value == "contextual_difference"
    assert RelationshipType.EXTRACTION_FAILURE.value == "extraction_failure"


def test_document_status_enum():
    """Verify document lifecycle status values."""
    assert DocumentStatus.PROCESSED.value == "processed"
    assert DocumentStatus.EXTRACTING.value == "extracting"
    assert DocumentStatus.ERROR.value == "error"


def test_fact_creation_valid():
    """Test standard fact instantiation with defaults."""
    fact = Fact(
        id="fact_001",
        statement="India's real GDP grew by 8.2% in FY24.",
        value="8.2",
        unit="%",
        category="Macroeconomics",
        confidence=0.95,
        source_doc_id="doc_01",
        source_doc_name="Economic Survey 2024",
        page_numbers=[12],
        evidence_text="Real GDP growth was recorded at 8.2 per cent in 2023-24.",
    )
    assert fact.id == "fact_001"
    assert fact.confidence == 0.95
    assert fact.category == "Macroeconomics"
    assert isinstance(fact.context, Context)


def test_fact_confidence_out_of_bounds():
    """Ensure confidence outside [0.0, 1.0] raises a validation error."""
    with pytest.raises(ValidationError):
        Fact(id="invalid_1", statement="Test statement", confidence=1.5)

    with pytest.raises(ValidationError):
        Fact(id="invalid_2", statement="Test statement", confidence=-0.1)


def test_context_defaults():
    """Test that Context initializes with empty string defaults."""
    ctx = Context()
    assert ctx.time_period == ""
    assert ctx.scope == ""
    assert ctx.methodology == ""


def test_relationship_creation():
    """Test valid relationship instantiation between two facts."""
    rel = Relationship(
        id="rel_001",
        fact_a_id="fact_001",
        fact_b_id="fact_002",
        relationship_type=RelationshipType.CORROBORATES.value,
        explanation="Both documents cite 8.2% GDP growth for FY24.",
        confidence=0.98,
        reconciliation="Full alignment between official statistical reporting.",
    )
    assert rel.id == "rel_001"
    assert rel.fact_a_id == "fact_001"
    assert rel.fact_b_id == "fact_002"
    assert rel.relationship_type == "corroborates"
    assert rel.confidence == 0.98


def test_document_model():
    """Test document metadata schema."""
    doc = Document(
        id="doc_rbi_24",
        filename="rbi_annual_report_24.pdf",
        original_filename="RBI_Annual_Report.pdf",
        page_count=45,
        fact_count=18,
        status="processed",
    )
    assert doc.id == "doc_rbi_24"
    assert doc.page_count == 45
    assert doc.status == "processed"


def test_knowledge_layer_stats():
    """Test dashboard aggregation schema."""
    stats = KnowledgeLayerStats(
        total_documents=3,
        total_facts=42,
        total_relationships=12,
        corroborations=6,
        contradictions=2,
        contextual_differences=4,
        avg_confidence=0.91,
    )
    assert stats.total_documents == 3
    assert stats.total_facts == 42
    assert stats.corroborations == 6
    assert stats.avg_confidence == 0.91
