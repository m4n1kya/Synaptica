"""
Unit tests with mocking for Synaptica multi-tenant Firestore persistence layer.
"""
from unittest.mock import MagicMock, patch
from models import Document, Fact, Relationship


@patch("firestore_store.get_db")
def test_firestore_store_init_and_paths(mock_get_db):
    """Verify FirestoreStore correctly scopes collections under /users/{user_id}."""
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    from firestore_store import FirestoreStore
    store = FirestoreStore("user_123")

    mock_db.collection.assert_called_with("users")
    mock_db.collection().document.assert_called_with("user_123")
    assert store.user_id == "user_123"


@patch("firestore_store.get_db")
def test_firestore_store_add_document(mock_get_db):
    """Verify add_document sets document data in Firestore."""
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    from firestore_store import FirestoreStore
    store = FirestoreStore("user_123")

    doc = Document(id="doc_test", filename="test.pdf", page_count=5)
    result = store.add_document(doc)

    assert result.id == "doc_test"
    doc_ref = store.user_ref.collection().document()
    doc_ref.set.assert_called_once()


@patch("firestore_store.get_db")
def test_firestore_store_add_fact(mock_get_db):
    """Verify add_fact sets fact data and increments parent document fact_count."""
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    from firestore_store import FirestoreStore
    store = FirestoreStore("user_123")

    # Mock parent document snapshot existing with count 3
    doc_snap = MagicMock()
    doc_snap.exists = True
    doc_snap.to_dict.return_value = {"fact_count": 3}
    store.user_ref.collection().document().get.return_value = doc_snap

    fact = Fact(id="f_test", statement="Sample fact", source_doc_id="doc_test")
    result = store.add_fact(fact)

    assert result.id == "f_test"
    # Verify doc count updated to 4
    store.user_ref.collection().document().update.assert_called_with({"fact_count": 4})


@patch("firestore_store.get_db")
def test_firestore_store_delete_document_not_found(mock_get_db):
    """Verify delete_document returns False if document does not exist."""
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    from firestore_store import FirestoreStore
    store = FirestoreStore("user_123")

    doc_snap = MagicMock()
    doc_snap.exists = False
    store.user_ref.collection().document().get.return_value = doc_snap

    result = store.delete_document("missing_doc")
    assert result is False


@patch("firestore_store.get_db")
def test_firestore_store_delete_document_cascade(mock_get_db):
    """Verify delete_document deletes doc, associated facts, and relationships."""
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    from firestore_store import FirestoreStore
    store = FirestoreStore("user_123")

    # Mock doc exists
    doc_snap = MagicMock()
    doc_snap.exists = True
    doc_ref = MagicMock()
    doc_ref.get.return_value = doc_snap
    store.user_ref.collection().document.return_value = doc_ref

    # Mock facts query returning one fact
    mock_fact = MagicMock()
    mock_fact.id = "f_1"
    store.user_ref.collection().where().stream.return_value = [mock_fact]

    # Mock relationships query returning one linked rel
    mock_rel = MagicMock()
    mock_rel.to_dict.return_value = {"fact_a_id": "f_1", "fact_b_id": "other_f"}
    store.user_ref.collection().stream.return_value = [mock_rel]

    result = store.delete_document("doc_test")
    assert result is True
    doc_ref.delete.assert_called_once()
    mock_fact.reference.delete.assert_called_once()
    mock_rel.reference.delete.assert_called_once()


@patch("firestore_store.get_db")
def test_firestore_store_get_cases(mock_get_db):
    """Verify get_cases returns an empty list for per-user workspaces."""
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    from firestore_store import FirestoreStore
    store = FirestoreStore("user_123")
    assert store.get_cases() == []


@patch("firestore_store.get_db")
def test_firestore_store_add_relationship(mock_get_db):
    """Verify add_relationship stores relationship document in Firestore."""
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    from firestore_store import FirestoreStore
    store = FirestoreStore("user_123")

    rel = Relationship(
        id="rel_abc",
        fact_a_id="fa",
        fact_b_id="fb",
        relationship_type="corroborates",
        explanation="Consistent reports",
        confidence=0.9
    )
    result = store.add_relationship(rel)

    assert result.id == "rel_abc"
    rel_ref = store.user_ref.collection().document()
    rel_ref.set.assert_called_once_with(rel.model_dump())


@patch("firestore_store.get_db")
def test_firestore_store_get_all_documents(mock_get_db):
    """Verify get_all_documents streams and parses documents."""
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    from firestore_store import FirestoreStore
    store = FirestoreStore("user_123")

    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {
        "id": "doc_stream_1",
        "filename": "annual_filing.pdf",
        "total_pages": 12,
        "status": "processed"
    }
    store.user_ref.collection().stream.return_value = [mock_doc]

    docs = store.get_all_documents()
    assert len(docs) == 1
    assert docs[0].id == "doc_stream_1"
    assert docs[0].filename == "annual_filing.pdf"


@patch("firestore_store.get_db")
def test_firestore_store_get_all_facts_filtered(mock_get_db):
    """Verify get_all_facts applies category, doc_id, and min_confidence filters."""
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    from firestore_store import FirestoreStore
    store = FirestoreStore("user_123")

    mock_fact = MagicMock()
    mock_fact.to_dict.return_value = {
        "id": "fact_stream_1",
        "statement": "EBITDA increased 24%",
        "category": "Profitability",
        "source_doc_id": "doc_1",
        "confidence": 0.88
    }
    # Mock chain: query.where().where().where().stream()
    query_mock = store.user_ref.collection()
    query_mock.where.return_value = query_mock
    query_mock.stream.return_value = [mock_fact]

    facts = store.get_all_facts(category="Profitability", doc_id="doc_1", min_confidence=0.8)
    assert len(facts) == 1
    assert facts[0].id == "fact_stream_1"
    assert facts[0].statement == "EBITDA increased 24%"


@patch("firestore_store.get_db")
def test_firestore_store_get_relationships_filtered(mock_get_db):
    """Verify get_relationships filters by minimum confidence score."""
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    from firestore_store import FirestoreStore
    store = FirestoreStore("user_123")

    mock_rel = MagicMock()
    mock_rel.to_dict.return_value = {
        "id": "rel_stream_1",
        "fact_a_id": "fa",
        "fact_b_id": "fb",
        "relationship_type": "contradicts",
        "confidence": 0.95
    }
    query_mock = store.user_ref.collection()
    query_mock.where.return_value = query_mock
    query_mock.stream.return_value = [mock_rel]

    rels = store.get_relationships(min_confidence=0.9)
    assert len(rels) == 1
    assert rels[0].id == "rel_stream_1"
    assert rels[0].relationship_type == "contradicts"


@patch("firestore_store.get_db")
def test_firestore_store_get_category_distribution(mock_get_db):
    """Verify FirestoreStore.get_category_distribution correctly aggregates categories."""
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    from firestore_store import FirestoreStore
    from models import Fact
    store = FirestoreStore("user_cat_test")
    f1 = Fact(id="f1", statement="Fact 1", category="Economy")
    f2 = Fact(id="f2", statement="Fact 2", category="Economy")
    f3 = Fact(id="f3", statement="Fact 3", category="Logistics")

    with patch.object(store, "get_all_facts", return_value=[f1, f2, f3]):
        dist = store.get_category_distribution()

    assert dist == {"Economy": 2, "Logistics": 1}


