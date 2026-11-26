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

    @property
    def confidence_percentage(self) -> float:
        """Return confidence as a percentage float rounded to 1 decimal place."""
        return round(self.confidence * 100, 1)

    @property
    def word_count(self) -> int:
        """Return the count of words in the statement text."""
        return len(self.statement.split()) if self.statement else 0

    @property
    def evidence_word_count(self) -> int:
        """Return the count of words in the evidence quote."""
        return len(self.evidence_text.split()) if self.evidence_text else 0

    def statement_summary(self, max_length: int = 80) -> str:
        """Produce a truncated statement summary for compact UI display."""
        text = self.statement.strip()
        if len(text) <= max_length:
            return text
        return text[: max_length - 3].rstrip() + "..."

    def is_equivalent(self, other: "Fact") -> bool:
        """Check if two facts assert identical claims based on normalized statement or value/unit in the same category."""
        if not isinstance(other, Fact):
            return False
        if self.statement.strip().lower() == other.statement.strip().lower():
            return True
        if (self.category.strip().lower() == other.category.strip().lower() and
            self.value and other.value and
            self.value.strip() == other.value.strip() and
            (self.unit or "").strip().lower() == (other.unit or "").strip().lower()):
            return True
        return False

    def to_export_dict(self) -> dict:
        """Serialize fact with computed presentation fields (citation, confidence percentage)."""
        data = self.model_dump()
        data["citation"] = self.formatted_citation()
        data["confidence_percentage"] = self.confidence_percentage
        data["is_numeric"] = self.is_numeric()
        data["word_count"] = self.word_count
        data["statement_summary"] = self.statement_summary()
        return data


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

    @property
    def confidence_percentage(self) -> float:
        """Return confidence as a percentage float rounded to 1 decimal place."""
        return round(self.confidence * 100, 1)

    def is_cross_document(self, fact_a: "Fact", fact_b: "Fact") -> bool:
        """Verify whether the linked facts originate from distinct source documents."""
        return fact_a.source_doc_id != fact_b.source_doc_id

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

    @property
    def is_epistemic_conflict(self) -> bool:
        """Indicate whether this relationship represents an analytical discrepancy or contradiction."""
        return self.relationship_type in ("contradicts", "contextual_difference")

    def summary_label(self) -> str:
        """Produce a formatted indicator badge string for UI and exports."""
        return f"[{self.relationship_type.upper()}] ({self.confidence_percentage}%)"

    def to_export_dict(self) -> dict:
        """Serialize relationship with computed presentation fields."""
        data = self.model_dump()
        data["confidence_percentage"] = self.confidence_percentage
        data["is_epistemic_conflict"] = self.is_epistemic_conflict
        data["summary_label"] = self.summary_label()
        return data


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

    def formatted_display_name(self) -> str:
        """Return the preferred human-readable title or fallback filename."""
        if self.original_filename and self.original_filename.strip():
            return self.original_filename.strip()
        return self.filename

    def to_export_dict(self) -> dict:
        """Serialize document with computed presentation fields."""
        data = self.model_dump()
        data["display_name"] = self.formatted_display_name()
        data["is_ready"] = self.is_ready()
        return data


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

    def summary_brief(self) -> str:
        """Return a formatted title and case type summary."""
        return f"[{self.case_type.upper()}] {self.title}"


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
