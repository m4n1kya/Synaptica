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
    CaseStudy,
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


def test_fact_helper_methods():
    """Test Fact helper methods: is_numeric, formatted_citation, and has_context."""
    fact_num = Fact(
        id="fact_num",
        statement="Inflation fell to 4.8%",
        value="4.8%",
        source_doc_name="RBI Bulletin",
        page_numbers=[3, 1, 3, -5, 0],
        context=Context(time_period="FY24", scope="National", methodology="CPI"),
    )
    assert fact_num.is_numeric() is True
    assert fact_num.page_numbers == [1, 3]  # sanitized: positive, unique, sorted
    assert fact_num.formatted_citation() == "RBI Bulletin (p. 1, 3)"
    assert fact_num.has_context() is True

    fact_text = Fact(
        id="fact_text",
        statement="Monetary policy stance was neutral",
        value="neutral",
        source_doc_name="Policy Statement",
        page_numbers=[],
    )
    assert fact_text.is_numeric() is False
    assert fact_text.formatted_citation() == "Policy Statement"
    assert fact_text.has_context() is False

    fact_curr = Fact(
        id="fact_curr",
        statement="Revenue reached $1,250.50",
        value="$1,250.50",
    )
    assert fact_curr.is_numeric() is True
    assert fact_curr.formatted_citation() == "Unknown Source"


def test_relationship_helper_methods():
    """Test Relationship helper methods: involves_fact and get_counterpart_id."""
    rel = Relationship(
        id="rel_ab",
        fact_a_id="fact_1",
        fact_b_id="fact_2",
        relationship_type="corroborates",
    )
    assert rel.involves_fact("fact_1") is True
    assert rel.involves_fact("fact_2") is True
    assert rel.involves_fact("fact_3") is False

    assert rel.get_counterpart_id("fact_1") == "fact_2"
    assert rel.get_counterpart_id("fact_2") == "fact_1"
    assert rel.get_counterpart_id("fact_3") is None


def test_document_is_ready():
    """Test Document.is_ready() helper method."""
    doc_done = Document(id="doc_1", filename="a.pdf", status="processed")
    assert doc_done.is_ready() is True

    doc_pending = Document(id="doc_2", filename="b.pdf", status="parsing")
    assert doc_pending.is_ready() is False


def test_fact_page_numbers_sanitization_scalar_and_invalid():
    """Test page_numbers sanitization with scalar values and mixed non-integer inputs."""
    fact_scalar_int = Fact(id="f_s1", statement="Scalar int page", page_numbers=5)
    assert fact_scalar_int.page_numbers == [5]

    fact_scalar_str = Fact(id="f_s2", statement="Scalar str page", page_numbers="12")
    assert fact_scalar_str.page_numbers == [12]

    fact_mixed = Fact(id="f_s3", statement="Mixed invalid", page_numbers=["1", "invalid_page", None, -2, 7])
    assert fact_mixed.page_numbers == [1, 7]


def test_fact_citation_pages_only():
    """Test formatted_citation when source_doc_name is empty but page numbers exist."""
    fact = Fact(id="f_p", statement="Only pages", source_doc_name="", page_numbers=[4, 2])
    assert fact.formatted_citation() == "p. 2, 4"


def test_confidence_percentage_and_cross_document():
    """Test confidence_percentage property and is_cross_document relationship check."""
    f1 = Fact(id="f1", statement="Claim 1", confidence=0.854, source_doc_id="doc_a")
    f2 = Fact(id="f2", statement="Claim 2", confidence=0.927, source_doc_id="doc_b")
    f3 = Fact(id="f3", statement="Claim 3", confidence=0.75, source_doc_id="doc_a")

    assert f1.confidence_percentage == 85.4
    assert f2.confidence_percentage == 92.7

    rel = Relationship(id="r1", fact_a_id="f1", fact_b_id="f2", relationship_type="corroborates", confidence=0.916)
    assert rel.confidence_percentage == 91.6
    assert rel.is_cross_document(f1, f2) is True
    assert rel.is_cross_document(f1, f3) is False


def test_fact_is_equivalent_and_export_dict():
    """Verify is_equivalent checks statement/metric alignment and to_export_dict serializes presentation fields."""
    f1 = Fact(id="f1", statement="Real GDP grew by 8.2%", value="8.2", unit="%", category="Macroeconomics", confidence=0.95, page_numbers=[12], source_doc_name="Doc1")
    f2 = Fact(id="f2", statement="real gdp grew by 8.2% ", value="8.2", unit="%", category="Macroeconomics", confidence=0.9)
    f3 = Fact(id="f3", statement="Different phrasing", value="8.2", unit="%", category="Macroeconomics", confidence=0.92)
    f4 = Fact(id="f4", statement="Inflation reached 5%", value="5.0", unit="%", category="Inflation", confidence=0.88)

    assert f1.is_equivalent(f2) is True
    assert f1.is_equivalent(f3) is True
    assert f1.is_equivalent(f4) is False
    assert f1.is_equivalent("not a fact") is False

    export = f1.to_export_dict()
    assert export["citation"] == "Doc1 (p. 12)"
    assert export["confidence_percentage"] == 95.0
    assert export["is_numeric"] is True


def test_case_study_summary_brief():
    """Verify CaseStudy.summary_brief formatting."""
    case = CaseStudy(id="c1", title="GDP Growth Validation", case_type="corroboration")
    assert case.summary_brief() == "[CORROBORATION] GDP Growth Validation"


def test_fact_word_count_and_statement_summary():
    """Verify Fact.word_count, evidence_word_count, and statement_summary truncation."""
    short_fact = Fact(
        id="f_w1",
        statement="Revenue increased significantly in Q3.",
        evidence_text="As reported on page 5, overall revenue rose.",
    )
    assert short_fact.word_count == 5
    assert short_fact.evidence_word_count == 8
    assert short_fact.statement_summary(50) == "Revenue increased significantly in Q3."

    long_fact = Fact(
        id="f_w2",
        statement="The quarterly consolidated operating income margin increased by approximately 240 basis points year over year across all regions.",
    )
    assert long_fact.word_count == 18
    summary = long_fact.statement_summary(40)
    assert len(summary) <= 40
    assert summary.endswith("...")
    assert "consolidated" in summary

    # Export dictionary includes these fields
    export_dict = long_fact.to_export_dict()
    assert export_dict["word_count"] == 18
    assert "statement_summary" in export_dict


def test_relationship_conflict_and_export_dict():
    """Verify Relationship.is_epistemic_conflict, summary_label, and to_export_dict."""
    r_corrob = Relationship(
        id="rel_c",
        fact_a_id="fa",
        fact_b_id="fb",
        relationship_type="corroborates",
        confidence=0.925
    )
    assert r_corrob.is_epistemic_conflict is False
    assert r_corrob.summary_label() == "[CORROBORATES] (92.5%)"

    r_contra = Relationship(
        id="rel_x",
        fact_a_id="fa",
        fact_b_id="fc",
        relationship_type="contradicts",
        confidence=0.88
    )
    assert r_contra.is_epistemic_conflict is True
    assert r_contra.summary_label() == "[CONTRADICTS] (88.0%)"

    r_context = Relationship(
        id="rel_d",
        fact_a_id="fa",
        fact_b_id="fd",
        relationship_type="contextual_difference",
        confidence=0.85
    )
    assert r_context.is_epistemic_conflict is True

    export = r_contra.to_export_dict()
    assert export["confidence_percentage"] == 88.0
    assert export["is_epistemic_conflict"] is True
    assert export["summary_label"] == "[CONTRADICTS] (88.0%)"


def test_document_display_name_and_export_dict():
    """Verify Document.formatted_display_name and to_export_dict presentation fields."""
    doc_named = Document(
        id="doc_1",
        filename="01-sample-report.pdf",
        original_filename="Annual Financial Report 2024",
        status="processed",
    )
    assert doc_named.formatted_display_name() == "Annual Financial Report 2024"
    export_named = doc_named.to_export_dict()
    assert export_named["display_name"] == "Annual Financial Report 2024"
    assert export_named["is_ready"] is True

    doc_fallback = Document(
        id="doc_2",
        filename="unnamed-doc.pdf",
        original_filename="",
        status="parsing",
    )
    assert doc_fallback.formatted_display_name() == "unnamed-doc.pdf"
    export_fallback = doc_fallback.to_export_dict()
    assert export_fallback["display_name"] == "unnamed-doc.pdf"
    assert export_fallback["is_ready"] is False





