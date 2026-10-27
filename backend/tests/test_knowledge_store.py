"""
Unit tests for Synaptica in-memory KnowledgeStore operations, querying, and cascade deletion.
"""
from knowledge_store import KnowledgeStore
from models import Document, Fact, Relationship


def test_knowledge_store_empty_init():
    """Verify clean initialization when load_demo=False."""
    store = KnowledgeStore(load_demo=False)
    assert len(store.get_all_documents()) == 0
    assert len(store.get_all_facts()) == 0
    assert len(store.get_all_relationships()) == 0


def test_knowledge_store_demo_init():
    """Verify pre-computed demo data is loaded when load_demo=True."""
    store = KnowledgeStore(load_demo=True)
    assert len(store.get_all_documents()) == 6
    assert len(store.get_all_facts()) >= 20
    assert len(store.get_all_relationships()) >= 5
    assert len(store.cases) == 4


def test_knowledge_store_add_and_retrieve():
    """Verify basic CRUD additions and retrieval in an empty KnowledgeStore."""
    store = KnowledgeStore(load_demo=False)
    doc = Document(id="doc_1", filename="doc1.pdf", page_count=10)
    fact = Fact(id="f1", statement="Revenue grew 20%", category="Revenue", source_doc_id="doc_1", confidence=0.9)
    rel = Relationship(
        id="r1",
        fact_a_id="f1",
        fact_b_id="f2",
        relationship_type="corroborates",
        explanation="Agreement",
        confidence=0.95
    )

    store.add_document(doc)
    store.add_fact(fact)
    store.add_relationship(rel)

    assert len(store.get_all_documents()) == 1
    assert len(store.get_all_facts()) == 1
    assert len(store.get_all_relationships()) == 1
    assert len(store.get_relationships()) == 1


def test_knowledge_store_cascade_deletion():
    """Verify deleting a document cascades to delete its facts and linked relationships."""
    store = KnowledgeStore(load_demo=False)
    doc1 = Document(id="doc_1", filename="doc1.pdf")
    doc2 = Document(id="doc_2", filename="doc2.pdf")

    fact1 = Fact(id="f1", statement="Fact 1", source_doc_id="doc_1")
    fact2 = Fact(id="f2", statement="Fact 2", source_doc_id="doc_2")

    # Relationship linking fact1 (from doc1) and fact2 (from doc2)
    rel = Relationship(id="r1", fact_a_id="f1", fact_b_id="f2", relationship_type="corroborates")

    store.add_document(doc1)
    store.add_document(doc2)
    store.add_fact(fact1)
    store.add_fact(fact2)
    store.add_relationship(rel)

    assert len(store.get_all_facts()) == 2
    assert len(store.get_all_relationships()) == 1

    # Delete doc1: fact1 should be deleted, and r1 should be deleted
    deleted = store.delete_document("doc_1")
    assert deleted is True

    # Remaining state
    assert len(store.get_all_documents()) == 1
    remaining_facts = store.get_all_facts()
    assert len(remaining_facts) == 1
    assert remaining_facts[0].id == "f2"

    # Relationship should have been cascade-deleted
    assert len(store.get_all_relationships()) == 0

    # Non-existent document returns False
    assert store.delete_document("non_existent") is False


def test_knowledge_store_filtering():
    """Verify querying facts and relationships with category and confidence filters."""
    store = KnowledgeStore(load_demo=False)
    f1 = Fact(id="f1", statement="Inflation at 5%", category="Inflation", source_doc_id="d1", confidence=0.8)
    f2 = Fact(id="f2", statement="GDP at 7%", category="Macroeconomics", source_doc_id="d1", confidence=0.95)
    f3 = Fact(id="f3", statement="Low confidence fact", category="Inflation", source_doc_id="d2", confidence=0.4)

    store.add_fact(f1)
    store.add_fact(f2)
    store.add_fact(f3)

    # Filter by category
    inflation_facts = store.get_all_facts(category="Inflation")
    assert len(inflation_facts) == 2

    # Filter by doc_id
    doc2_facts = store.get_all_facts(doc_id="d2")
    assert len(doc2_facts) == 1
    assert doc2_facts[0].id == "f3"

    # Filter by min_confidence
    high_conf = store.get_all_facts(min_confidence=0.85)
    assert len(high_conf) == 1
    assert high_conf[0].id == "f2"


def test_knowledge_store_get_fact_with_relationships():
    """Verify retrieving a fact along with all linked graph edges."""
    store = KnowledgeStore(load_demo=False)
    f1 = Fact(id="f1", statement="Fact A", source_doc_id="d1")
    f2 = Fact(id="f2", statement="Fact B", source_doc_id="d2")
    rel = Relationship(id="r1", fact_a_id="f1", fact_b_id="f2", relationship_type="contradicts")

    store.add_fact(f1)
    store.add_fact(f2)
    store.add_relationship(rel)

    details = store.get_fact_with_relationships("f1")
    assert details is not None
    assert details["fact"].id == "f1"
    assert len(details["related"]) == 1
    assert details["related"][0]["fact"].id == "f2"
    assert details["related"][0]["relationship"].id == "r1"

    # Non-existent fact returns None
    assert store.get_fact_with_relationships("non_existent") is None


def test_knowledge_store_stats_calculation():
    """Verify aggregated metrics and distribution computations in get_stats."""
    store = KnowledgeStore(load_demo=False)
    doc = Document(id="d1", filename="report.pdf")
    f1 = Fact(id="f1", statement="Fact 1", category="Revenue", source_doc_id="d1", confidence=0.8)
    f2 = Fact(id="f2", statement="Fact 2", category="Revenue", source_doc_id="d1", confidence=0.9)
    rel = Relationship(id="r1", fact_a_id="f1", fact_b_id="f2", relationship_type="corroborates")

    store.add_document(doc)
    store.add_fact(f1)
    store.add_fact(f2)
    store.add_relationship(rel)

    stats = store.get_stats()
    assert stats.total_documents == 1
    assert stats.total_facts == 2
    assert stats.total_relationships == 1
    assert stats.corroborations == 1
    assert stats.contradictions == 0
    assert stats.categories.get("Revenue") == 2
    assert abs(stats.avg_confidence - 0.85) < 1e-4
