import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Optional
from models import Fact, Relationship, Document, CaseStudy
import os
import json

# Initialize Firebase Admin once
if not firebase_admin._apps:
    cred_path = os.path.join(os.path.dirname(__file__), 'firebase-adminsdk.json')
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    elif os.environ.get("FIREBASE_SERVICE_ACCOUNT"):
        cert_dict = json.loads(os.environ.get("FIREBASE_SERVICE_ACCOUNT"))
        cred = credentials.Certificate(cert_dict)
        firebase_admin.initialize_app(cred)
    else:
        # Fallback (will likely fail on firestore.client() if no default creds exist)
        try:
            firebase_admin.initialize_app()
        except Exception:
            pass

def get_db():
    return firestore.client()

class FirestoreStore:
    def __init__(self, user_id: str):
        self.user_id = user_id
        db = get_db()
        self.user_ref = db.collection('users').document(user_id)

    def add_document(self, doc: Document) -> Document:
        doc_dict = doc.model_dump()
        self.user_ref.collection('documents').document(doc.id).set(doc_dict)
        return doc

    def add_fact(self, fact: Fact) -> Fact:
        fact_dict = fact.model_dump()
        self.user_ref.collection('facts').document(fact.id).set(fact_dict)
        # Update doc fact count
        doc_ref = self.user_ref.collection('documents').document(fact.source_doc_id)
        doc_snap = doc_ref.get()
        if doc_snap.exists:
            count = doc_snap.to_dict().get('fact_count', 0)
            doc_ref.update({'fact_count': count + 1})
        return fact

    def add_relationship(self, rel: Relationship) -> Relationship:
        rel_dict = rel.model_dump()
        self.user_ref.collection('relationships').document(rel.id).set(rel_dict)
        return rel

    def delete_document(self, doc_id: str) -> bool:
        doc_ref = self.user_ref.collection('documents').document(doc_id)
        if not doc_ref.get().exists:
            return False
            
        doc_ref.delete()
        
        # Delete facts
        facts_query = self.user_ref.collection('facts').where('source_doc_id', '==', doc_id).stream()
        fact_ids = set()
        for f in facts_query:
            fact_ids.add(f.id)
            f.reference.delete()
            
        # Delete relationships referencing those facts
        if fact_ids:
            rels = self.user_ref.collection('relationships').stream()
            for r in rels:
                r_data = r.to_dict()
                if r_data.get('fact_a_id') in fact_ids or r_data.get('fact_b_id') in fact_ids:
                    r.reference.delete()
                    
        return True

    def get_all_documents(self) -> List[Document]:
        docs = []
        for doc in self.user_ref.collection('documents').stream():
            docs.append(Document(**doc.to_dict()))
        return docs

    def get_all_facts(self, category: Optional[str] = None, 
                      doc_id: Optional[str] = None,
                      min_confidence: float = 0.0) -> List[Fact]:
        query = self.user_ref.collection('facts')
        if category:
            query = query.where('category', '==', category)
        if doc_id:
            query = query.where('source_doc_id', '==', doc_id)
        if min_confidence > 0:
            query = query.where('confidence', '>=', min_confidence)
            
        facts = []
        for f in query.stream():
            facts.append(Fact(**f.to_dict()))
        return facts

    def get_relationships(self, min_confidence: float = 0.0) -> List[Relationship]:
        query = self.user_ref.collection('relationships')
        if min_confidence > 0:
            query = query.where('confidence', '>=', min_confidence)
            
        rels = []
        for r in query.stream():
            rels.append(Relationship(**r.to_dict()))
        return rels
        
    def get_cases(self) -> List[CaseStudy]:
        # Return empty list as cases are not currently generated per user
        return []
