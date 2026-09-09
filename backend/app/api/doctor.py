"""
Doctor Assistant Route Placeholders.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/doctor", tags=["Doctor Assistant"])


class ConsultationNoteRequest(BaseModel):
    patient_id: str
    doctor_id: str
    notes: str
    confirmed_findings: Optional[str] = None


class DoctorQueryRequest(BaseModel):
    patient_id: str
    doctor_id: str
    query: str


@router.get("/patients")
async def list_patients():
    """Doctor patient search placeholder."""
    return {
        "patients": [
            {"patient_id": "PAT-89210", "name": "Demo Patient A", "last_visit": "2026-09-01"},
            {"patient_id": "PAT-93104", "name": "Demo Patient B", "last_visit": "2026-08-28"}
        ]
    }


@router.get("/retrieval/{patient_id}")
async def retrieve_longitudinal_context(patient_id: str):
    """Retrieve historical context for doctor review placeholder."""
    return {
        "patient_id": patient_id,
        "historical_context": [],
        "message": "Doctor context retrieval logic scheduled for Days 12-15."
    }


@router.post("/consultation")
async def add_consultation_note(payload: ConsultationNoteRequest):
    """Save doctor consultation notes and confirmed clinical findings placeholder."""
    return {
        "status": "success",
        "patient_id": payload.patient_id,
        "record_type": "doctor_confirmed",
        "message": "Consultation note saved (Placeholder Day 1)."
    }


@router.post("/assist")
async def doctor_ai_assist(payload: DoctorQueryRequest):
    """Doctor AI discussion endpoint placeholder."""
    return {
        "reply": f"[Doctor AI Placeholder] Answering doctor query for patient {payload.patient_id}. AI decision support scheduled for Days 12-15.",
        "disclaimer": "The final medical decision always belongs to the doctor."
    }
