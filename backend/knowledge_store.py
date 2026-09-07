"""
Synaptica — Knowledge Store
In-memory store with JSON persistence for documents, facts, and relationships.
"""
import json
import os
from typing import List, Optional, Dict
from models import Fact, Relationship, Document, CaseStudy, KnowledgeLayerStats
from demo_data import get_demo_documents, get_demo_facts, get_demo_relationships, get_demo_cases


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "knowledge")


class KnowledgeStore:
    """Central store for the fact knowledge layer."""

    def __init__(self, load_demo: bool = True):
        self.documents: Dict[str, Document] = {}
        self.facts: Dict[str, Fact] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.cases: List[CaseStudy] = []

        os.makedirs(DATA_DIR, exist_ok=True)

        if load_demo:
            self._load_demo_data()

    def _load_demo_data(self):
        """Load pre-computed demo data for instant demonstration."""
        # Load documents
        for doc in get_demo_documents():
            self.documents[doc.id] = doc

        # Load facts
        for fact in get_demo_facts():
            self.facts[fact.id] = fact

        # Update document fact counts
        for doc_id in self.documents:
            count = sum(1 for f in self.facts.values() if f.source_doc_id == doc_id)
            self.documents[doc_id].fact_count = count

        # Load relationships
        for rel in get_demo_relationships():
            self.relationships[rel.id] = rel

        # Load case studies
        self.cases = get_demo_cases()

    def add_document(self, doc: Document) -> Document:
        self.documents[doc.id] = doc
        return doc

    def add_fact(self, fact: Fact) -> Fact:
        self.facts[fact.id] = fact
        # Update document fact count
        if fact.source_doc_id in self.documents:
            count = sum(1 for f in self.facts.values() if f.source_doc_id == fact.source_doc_id)
            self.documents[fact.source_doc_id].fact_count = count
        return fact

    def add_relationship(self, rel: Relationship) -> Relationship:
        self.relationships[rel.id] = rel
        return rel

    def delete_document(self, doc_id: str) -> bool:
        if doc_id not in self.documents:
            return False
        
        # Delete document
        del self.documents[doc_id]
        
        # Delete associated facts
        facts_to_delete = [f_id for f_id, f in self.facts.items() if f.source_doc_id == doc_id]
        for f_id in facts_to_delete:
            del self.facts[f_id]
            
        # Delete associated relationships
        rels_to_delete = [r_id for r_id, r in self.relationships.items() 
                          if r.fact_a_id in facts_to_delete or r.fact_b_id in facts_to_delete]
        for r_id in rels_to_delete:
            del self.relationships[r_id]
            
        return True

    def get_all_documents(self) -> List[Document]:
        return list(self.documents.values())

    def get_all_facts(self, category: Optional[str] = None, 
                      doc_id: Optional[str] = None,
                      min_confidence: float = 0.0) -> List[Fact]:
        facts = list(self.facts.values())
        if category:
            facts = [f for f in facts if f.category.lower() == category.lower()]
        if doc_id:
            facts = [f for f in facts if f.source_doc_id == doc_id]
        if min_confidence > 0:
            facts = [f for f in facts if f.confidence >= min_confidence]
        return facts

    def get_all_relationships(self, rel_type: Optional[str] = None) -> List[Relationship]:
        rels = list(self.relationships.values())
        if rel_type:
            rels = [r for r in rels if r.relationship_type == rel_type]
        return rels

    def get_fact_with_relationships(self, fact_id: str) -> Optional[dict]:
        fact = self.facts.get(fact_id)
        if not fact:
            return None
        related = [r for r in self.relationships.values() 
                   if r.fact_a_id == fact_id or r.fact_b_id == fact_id]
        # Get the related facts
        related_facts = []
        for r in related:
            other_id = r.fact_b_id if r.fact_a_id == fact_id else r.fact_a_id
            other_fact = self.facts.get(other_id)
            if other_fact:
                related_facts.append({"fact": other_fact, "relationship": r})
        return {"fact": fact, "related": related_facts}

    def get_stats(self) -> KnowledgeLayerStats:
        rels = list(self.relationships.values())
        categories = {}
        total_conf = 0.0
        for f in self.facts.values():
            categories[f.category] = categories.get(f.category, 0) + 1
            total_conf += f.confidence

        n_facts = len(self.facts)
        return KnowledgeLayerStats(
            total_documents=len(self.documents),
            total_facts=n_facts,
            total_relationships=len(rels),
            corroborations=sum(1 for r in rels if r.relationship_type == "corroborates"),
            contradictions=sum(1 for r in rels if r.relationship_type == "contradicts"),
            contextual_differences=sum(1 for r in rels if r.relationship_type == "contextual_difference"),
            extraction_failures=sum(1 for r in rels if r.relationship_type == "extraction_failure"),
            categories=categories,
            avg_confidence=round(total_conf / n_facts, 3) if n_facts > 0 else 0.0
        )

    def save_to_disk(self):
        """Persist current state to JSON files."""
        data = {
            "documents": [d.model_dump() for d in self.documents.values()],
            "facts": [f.model_dump() for f in self.facts.values()],
            "relationships": [r.model_dump() for r in self.relationships.values()],
        }
        path = os.path.join(DATA_DIR, "knowledge_layer.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_from_disk(self) -> bool:
        """Load state from persisted JSON."""
        path = os.path.join(DATA_DIR, "knowledge_layer.json")
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for d in data.get("documents", []):
            doc = Document(**d)
            self.documents[doc.id] = doc
        for f_data in data.get("facts", []):
            fact = Fact(**f_data)
            self.facts[fact.id] = fact
        for r in data.get("relationships", []):
            rel = Relationship(**r)
            self.relationships[rel.id] = rel
        return True
