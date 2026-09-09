"""
CCEE Data Schema Definitions.
Defines minimal structured representation for extracted clinical context.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ClinicalContextItem:
    """
    Represents a single compressed clinical context entry extracted from patient conversations
    or entered by a doctor.
    """
    patient_id: str
    category: str              # e.g., 'sleep', 'nutrition', 'stress', 'mood', 'activity'
    summary: str               # Compressed clinical summary (e.g. 'Reduced sleep associated with stress')
    source: str                # 'nutrition', 'mental_wellness', or 'doctor'
    record_type: str           # 'patient_reported' or 'doctor_confirmed'
    value: Optional[str] = None       # e.g. '5 hours/night'
    duration: Optional[str] = None    # e.g. '1 week'
    timestamp: Optional[str] = None   # ISO format timestamp string

    def to_dict(self) -> dict:
        """Converts item to clean dictionary, excluding empty optional fields."""
        data = {
            "patient_id": self.patient_id,
            "category": self.category,
            "summary": self.summary,
            "source": self.source,
            "record_type": self.record_type,
            "timestamp": self.timestamp or datetime.utcnow().isoformat()
        }
        if self.value:
            data["value"] = self.value
        if self.duration:
            data["duration"] = self.duration
        return data
