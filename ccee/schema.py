"""
CCEE Data Schema Definitions.
Defines minimal structured representation for extracted clinical context.
Freezes the minimal CCEE input/output contract for PCIF (Day 4 - Part A).

CCEE prioritizes meaningful context compression, not exhaustive entity extraction.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field

ALLOWED_SOURCES = ["nutrition", "mental_wellness"]

ALLOWED_RECORD_TYPES = ["patient_reported"]

ALLOWED_CATEGORIES = [
    "nutrition",
    "sleep",
    "stress",
    "mood",
    "hydration",
    "appetite",
    "activity",
    "symptom",
    "habit",
    "lifestyle_change",
    "other_clinically_relevant_context",
]

# Literal type alias for Pydantic schema validation
CategoryLiteral = Literal[
    "nutrition",
    "sleep",
    "stress",
    "mood",
    "hydration",
    "appetite",
    "activity",
    "symptom",
    "habit",
    "lifestyle_change",
    "other_clinically_relevant_context",
]


class ExtractedItem(BaseModel):
    """
    Pydantic model representing an individual context item for LLM structured output.
    Maps directly to the frozen ClinicalContextItem schema.
    """
    category: CategoryLiteral = Field(
        description="Clinical category classification matching frozen categories."
    )
    summary: str = Field(
        description="Concise, compressed clinical summary of the reported phenomenon. No medical diagnoses."
    )
    record_type: Literal["patient_reported"] = Field(
        default="patient_reported",
        description="Clinical validation status, strictly 'patient_reported'."
    )
    value: Optional[str] = Field(
        default=None,
        description="Optional quantitative or qualitative metric (e.g. '5 hours/night', '1 glass/day'). Omit if not mentioned."
    )
    duration: Optional[str] = Field(
        default=None,
        description="Optional reported duration or timeframe (e.g. '1 week', 'past 3 days'). Omit if not mentioned."
    )


class CCEEExtractionResult(BaseModel):
    """
    Pydantic container model for CCEE structured LLM output.
    """
    items: List[ExtractedItem] = Field(
        default_factory=list,
        description="List of extracted clinical context items. Must be empty [] if the conversation is non-clinical or irrelevant."
    )


@dataclass
class ClinicalContextItem:
    """
    Represents a single compressed clinical context entry extracted from patient conversations.
    Prioritizes meaningful context compression rather than exhaustive entity extraction.
    """
    category: str
    summary: str
    source: str
    record_type: str = "patient_reported"
    value: Optional[str] = None
    duration: Optional[str] = None

    def __post_init__(self):
        if not self.summary or not isinstance(self.summary, str) or not self.summary.strip():
            raise ValueError("Summary must be a non-empty string.")
        if self.source not in ALLOWED_SOURCES:
            raise ValueError(
                f"Invalid source '{self.source}'. Allowed sources: {ALLOWED_SOURCES}"
            )
        if self.record_type not in ALLOWED_RECORD_TYPES:
            raise ValueError(
                f"Invalid record_type '{self.record_type}'. Allowed record_types: {ALLOWED_RECORD_TYPES}"
            )
        if self.category not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"Invalid category '{self.category}'. Allowed categories: {ALLOWED_CATEGORIES}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Converts item to clean dictionary, excluding empty optional fields."""
        data: Dict[str, Any] = {
            "category": self.category,
            "summary": self.summary,
            "source": self.source,
            "record_type": self.record_type,
        }
        if self.value:
            data["value"] = self.value
        if self.duration:
            data["duration"] = self.duration
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClinicalContextItem":
        """Builds a ClinicalContextItem from a dictionary."""
        # Sanitize summary
        summary = data.get("summary")
        if summary is None or not isinstance(summary, str):
            summary = ""
        else:
            summary = summary.strip()

        # Sanitize value and duration: treat empty string or whitespace as None
        value = data.get("value")
        if value is not None and isinstance(value, str) and not value.strip():
            value = None
        duration = data.get("duration")
        if duration is not None and isinstance(duration, str) and not duration.strip():
            duration = None

        return cls(
            category=data.get("category", ""),
            summary=summary,
            source=data.get("source", ""),
            record_type=data.get("record_type", "patient_reported"),
            value=value,
            duration=duration,
        )


