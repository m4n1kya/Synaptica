"""
Synaptica — Core Data Models
Pydantic models for facts, relationships, documents, and the knowledge layer.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RelationshipType(str, Enum):
    CORROBORATES = "corroborates"
    CONTRADICTS = "contradicts"
    CONTEXTUAL_DIFFERENCE = "contextual_difference"
    EXTRACTION_FAILURE = "extraction_failure"


class DocumentStatus(str, Enum):
    UPLOADING = "uploading"
    PARSING = "parsing"
    EXTRACTING = "extracting"
    LINKING = "linking"
    PROCESSED = "processed"
    ERROR = "error"


class Context(BaseModel):
    """Temporal, scope, and methodological context for a fact."""
    time_period: str = ""
    scope: str = ""
    methodology: str = ""
    additional_notes: str = ""


class Fact(BaseModel):
    """An atomic factual claim extracted from a source document."""
    id: str
    statement: str
    value: Optional[str] = None
    unit: Optional[str] = None
    category: str = "General"
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    source_doc_id: str = ""
    source_doc_name: str = ""
    page_numbers: List[int] = []
    evidence_text: str = ""
    context: Context = Context()
    extracted_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    @field_validator("page_numbers", mode="before")
    @classmethod
    def sanitize_page_numbers(cls, v):
        if not v:
            return []
        if isinstance(v, (int, str)):
            v = [v]
        cleaned = []
        for p in v:
            try:
                num = int(p)
                if num > 0:
                    cleaned.append(num)
            except (ValueError, TypeError):
                continue
        return sorted(list(set(cleaned)))

    def is_numeric(self) -> bool:
        """Check if this fact holds an identifiable numeric value."""
        if not self.value:
            return False
        cleaned = self.value.strip().replace(",", "").replace("%", "").replace("$", "").replace("₹", "").replace("€", "").replace("£", "")
        try:
            float(cleaned)
            return True
        except ValueError:
            return False

    def formatted_citation(self) -> str:
        """Produce a clean human-readable document and page citation."""
        pages = ", ".join(str(p) for p in sorted(set(self.page_numbers)))
        if self.source_doc_name and pages:
            return f"{self.source_doc_name} (p. {pages})"
        if self.source_doc_name:
            return self.source_doc_name
        if pages:
            return f"p. {pages}"
        return "Unknown Source"

    def has_context(self) -> bool:
        """Determine if contextual metadata is populated."""
        return bool(self.context.time_period or self.context.scope or self.context.methodology)


class Relationship(BaseModel):
    """A discovered relationship between two facts across documents."""
    id: str
    fact_a_id: str
    fact_b_id: str
    relationship_type: str  # corroborates | contradicts | contextual_difference | extraction_failure
    explanation: str = ""
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    reconciliation: Optional[str] = None
    reasoning_trace: Optional[str] = None

    def involves_fact(self, fact_id: str) -> bool:
        """Check whether this relationship connects to a specific fact ID."""
        return fact_id in (self.fact_a_id, self.fact_b_id)

    def get_counterpart_id(self, fact_id: str) -> Optional[str]:
        """Return the other fact ID connected by this relationship, or None if not involved."""
        if fact_id == self.fact_a_id:
            return self.fact_b_id
        if fact_id == self.fact_b_id:
            return self.fact_a_id
        return None


class Document(BaseModel):
    """A processed PDF document in the knowledge layer."""
    id: str
    filename: str
    original_filename: str = ""
    page_count: int = 0
    fact_count: int = 0
    status: str = "processed"
    upload_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    dataset: str = ""  # "india-macroeconomy" or "delhivery"
    description: str = ""

    def is_ready(self) -> bool:
        """Check whether document processing has completed successfully."""
        return self.status == DocumentStatus.PROCESSED.value


class CaseStudy(BaseModel):
    """One of the four required demonstration cases."""
    id: str
    title: str
    case_type: str  # corroboration | contradiction | contextual | extraction_failure
    icon: str = ""
    summary: str = ""
    facts: List[Fact] = []
    relationships: List[Relationship] = []
    evidence_analysis: str = ""
    system_reasoning: str = ""


class KnowledgeLayerStats(BaseModel):
    """Dashboard statistics for the knowledge layer."""
    total_documents: int = 0
    total_facts: int = 0
    total_relationships: int = 0
    corroborations: int = 0
    contradictions: int = 0
    contextual_differences: int = 0
    extraction_failures: int = 0
    categories: dict = {}
    avg_confidence: float = 0.0
