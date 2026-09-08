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
    elif True:
        import base64
        cert_dict = json.loads(base64.b64decode("ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAic3luYXB0aWNhLW00bjFreWEiLAogICJwcml2YXRlX2tleV9pZCI6ICJhNDRiMjhhNzhiYzFiNDFiNmNmZTkyZTgzYTRkMjBhOGEyMDEzYWM5IiwKICAicHJpdmF0ZV9rZXkiOiAiLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdlFJQkFEQU5CZ2txaGtpRzl3MEJBUUVGQUFTQ0JLY3dnZ1NqQWdFQUFvSUJBUURJSXFHQnNnTmVaYVFqXG5YQlJUQWhaTU5IdDNyVjV0RHd3VW9lNkhORkgzcVVjZklzUjgvWjVCTTFBTmxsekowOWY0eDd4MzlCSllxZUVXXG5JanNCdXcyTlRNbDBTSmdOU0cvMGhmZmd6SzVzMFZ0TEw1S2RvSm9EbS9DZU5ONkVuZG95NzRjT3dWZXo1YXF4XG5aSEtuRC9vUjFQV1djK05jV2x6K1YrZktoT3RXMWFaTlJhSExlR0cwVDlIc3hVS2toVmFFd2FrZ2RZUk5aNzNaXG5CQzdSWEpiM1JxNGF1c1hjY2pwRGczU0gxYUZkQytwWXlkck5ua01PSjlmVitINVFaRTdJaVpJN1ZnN0lWaEk5XG5wMHk4Rkl1TlBsa0JZZ1RNNFFrNWpDcURsRGEwc1JzWGdPcm5TZkdVZ3ZNK3FOdkowVkY1Mnl3TU9RbWhScG43XG4xU2N1NHZpUEFnTUJBQUVDZ2dFQUJ3dUpDZXE5U1o1a1Y4WlBCTmtHOWVuSEN1QjBlWHhWSFlqUnY3cXN3LzRXXG5mZGNZZVpubjd6MmlMTWhGUGVtU0tiVEdRcWE1MnBzb1RFSXFONVpoRkw5R1BDeXVCWkd1TnpwY0RuTEdGUmlOXG5rU2o4alVYeEJmMkFTK0ZxajlxS3FzNVp2OEE0bVNHVmo2Y01qaXIyejVmaWlVaE5FWnd3dDlkYVZudTFXUm9lXG5PV0xJKzBldktLN2dKdWo5YWJtblpqN1N1RHM1V1pnekRLUXgwRkZEUWYxR3liZUVHaEZtajZweHlmYkh0ZlNSXG4rWGcrSWUzbWpyQnkrVDM5WGNKWXQxZFdYOXpFZ3AvOEtXV3dzQTFuZm01OWVmbHc3YmE2TVlkZUFkSjJseC9mXG42Q0txcC9wQnVyUGM0U3pmTy9LaFFmNm5DRHBPVDVrejZDVlJwbTkybVFLQmdRRDdiaXZxY2M3bnN2K1Mvby9xXG5hNHdUcnNKMVl5TDhCb0h0QUVCRE5QaDNESzdDTjRZTkF3eDFGN2Voa2Q1VWNIQkhmZ05meGhsWFVOaHVXa0FSXG5ManRrQ0FCVzhpNFRVRi90NGNOcEVLajZPREpJbmRhRVE4SEVMY21BMUtnVFk4bEM1M0VTTlNnSVlzTVpacmN6XG5GSytVUHVLRGl6RXUvSDIwdzE4K2FObWlSUUtCZ1FETHhjeU51d1JQUGdJa3hDTGphQVFmT2hCbjQwZDdiTW1QXG5ENnF1TUlYbjJhclBleFhrdWlrQWEzMkt5WVFuT1padHNuaG5ldXU3b0NBUkU3K3V2aG1OQlJ1RVkvNk01dnZ2XG5tMzJSbFRkMnQrdVBuYk5aa2JSclRRNjUrWENXR2V6eUNyYW5CYk15NFhSd3BKZ1FRbWhLaUZNME9XdHhQR3RMXG5ZZE42RGwvR3d3S0JnUUM5U1kwZ1hIdnpiWXdCWTBwL3BtWDNyM3JRbTBrTVNlM291bWFtOGlzWW5XQzM4TXNuXG40cUt2U0tMRHJhaWZFMk5FUDNkVTFEUGh5NGlWVTdhbCtKTlgxTHBFdXVDN1E2aGswN0drMkprT2Y5NURVeWpiXG52Sk1WR1k5NVFTQWtNTnlsVk02SWNhSm81Y21SeHdXbkhDeXZROFNPV2UwMlBYcDU2eGc2U1ArSHJRS0JnRXhHXG5EcW9palp0bnQzK3hsdW1PSHJUZGxCUis0MXZVdmFGNkdNWTR6WGFhYURCZmZ6TnRaem1NQXFMM2lTcnhpRmdwXG5USjVYU1hPaW5UNG5LVUdzVUg0VG9sZ3M0YlEySmFscmgxWCtCNU85aGtQc29KeHZTSnc5Ykx5NkhLVmlzT2xzXG5qeS8zbHpyOVh3dG00TEI5V3ZKREV2bmlZRkF6Y0duNEJTT1R5OC9uQW9HQWRteGdtMTVkTlo5OEw4dGx5UFNpXG5FSHVzc3prTE5uK21tS3E0cStRMGlJMGthazdmamU2THF4ZnFZcG5RQzlOTmlBOVBuczN5NXlvajdnV0Z2a3B4XG5MellBWU5KSmpIV2E1VENzUUxGUGg5dU9kaUp5MWprWW1iV2gvMHVCWTUxZytlUUh0WmFhcmRlL1lDdGdEQlozXG5IdGZZekZjV0hHejZIMFRiTnkxQ1JIbz1cbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsCiAgImNsaWVudF9lbWFpbCI6ICJmaXJlYmFzZS1hZG1pbnNkay1mYnN2Y0BzeW5hcHRpY2EtbTRuMWt5YS5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsCiAgImNsaWVudF9pZCI6ICIxMTQxNTA5NTMzMjcxNTUzODA5MzgiLAogICJhdXRoX3VyaSI6ICJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20vby9vYXV0aDIvYXV0aCIsCiAgInRva2VuX3VyaSI6ICJodHRwczovL29hdXRoMi5nb29nbGVhcGlzLmNvbS90b2tlbiIsCiAgImF1dGhfcHJvdmlkZXJfeDUwOV9jZXJ0X3VybCI6ICJodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9vYXV0aDIvdjEvY2VydHMiLAogICJjbGllbnRfeDUwOV9jZXJ0X3VybCI6ICJodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9yb2JvdC92MS9tZXRhZGF0YS94NTA5L2ZpcmViYXNlLWFkbWluc2RrLWZic3ZjJTQwc3luYXB0aWNhLW00bjFreWEuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K").decode("utf-8"))
        cred = credentials.Certificate(cert_dict)
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
