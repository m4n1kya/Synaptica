"""
Unit tests validating data integrity and referential constraints in Synaptica's benchmark datasets.
"""
from demo_data import (
    get_demo_documents,
    get_demo_facts,
    get_demo_relationships,
    get_demo_cases,
)
from models import RelationshipType


def test_demo_documents_structure():
    """Verify demo documents are well-formed with unique identifiers."""
    docs = get_demo_documents()
    assert len(docs) == 6, f"Expected 6 demo documents, got {len(docs)}"

    doc_ids = set()
    for doc in docs:
        assert doc.id, "Document ID must not be empty"
        assert doc.id not in doc_ids, f"Duplicate document ID: {doc.id}"
        doc_ids.add(doc.id)

        assert doc.filename.endswith(".pdf"), f"Document filename must be a PDF: {doc.filename}"
        assert doc.page_count > 0, f"Page count must be positive for {doc.id}"
        assert doc.dataset in ("india-macroeconomy", "delhivery"), f"Unexpected dataset: {doc.dataset}"
        assert doc.description, f"Document description missing for {doc.id}"


def test_demo_facts_integrity():
    """Verify demo facts have valid statements, citations, and confidence ranges."""
    facts = get_demo_facts()
    assert len(facts) >= 20, "Expected at least 20 extracted demo facts"

    docs = get_demo_documents()
    valid_doc_ids = {d.id for d in docs}
    fact_ids = set()

    for fact in facts:
        assert fact.id, "Fact ID must not be empty"
        assert fact.id not in fact_ids, f"Duplicate fact ID: {fact.id}"
        fact_ids.add(fact.id)

        assert fact.statement.strip(), f"Fact statement must not be empty: {fact.id}"
        assert 0.0 <= fact.confidence <= 1.0, f"Confidence out of bounds: {fact.confidence}"
        assert fact.source_doc_id in valid_doc_ids, f"Fact references invalid doc_id: {fact.source_doc_id}"
        assert len(fact.page_numbers) > 0, f"Fact must have page citations: {fact.id}"
        assert fact.evidence_text.strip(), f"Fact must have verbatim evidence: {fact.id}"


def test_demo_relationships_referential_integrity():
    """Verify that every relationship references valid, existing fact IDs."""
    facts = get_demo_facts()
    valid_fact_ids = {f.id for f in facts}
    relationships = get_demo_relationships()

    assert len(relationships) >= 5, "Expected demo relationships to be defined"
    valid_types = {e.value for e in RelationshipType}

    for rel in relationships:
        assert rel.id, "Relationship ID must not be empty"
        assert rel.relationship_type in valid_types, f"Invalid relationship type: {rel.relationship_type}"
        assert rel.fact_a_id in valid_fact_ids, f"fact_a_id '{rel.fact_a_id}' not found in demo facts"
        assert rel.fact_b_id in valid_fact_ids, f"fact_b_id '{rel.fact_b_id}' not found in demo facts"
        assert rel.fact_a_id != rel.fact_b_id, f"Self-referential relationship on {rel.id}"
        assert rel.explanation.strip(), f"Relationship explanation missing for {rel.id}"


def test_demo_case_studies():
    """Verify all four required demonstration case studies are populated."""
    cases = get_demo_cases()
    assert len(cases) == 4, f"Expected 4 core case studies, found {len(cases)}"

    case_types = {c.case_type for c in cases}
    assert "corroboration" in case_types
    assert "contradiction" in case_types
    assert "contextual" in case_types
    assert "extraction_failure" in case_types

    for case in cases:
        assert case.title, f"Case study title missing for {case.id}"
        assert len(case.facts) >= 1, f"Case study must contain facts: {case.id}"
        assert case.evidence_analysis, f"Evidence analysis missing for {case.id}"
        assert case.system_reasoning, f"System reasoning missing for {case.id}"
