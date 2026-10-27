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
