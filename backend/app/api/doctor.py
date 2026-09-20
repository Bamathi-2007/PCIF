import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.app.services.doctor_context_service import doctor_context_service

logger = logging.getLogger(__name__)

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


class DoctorContextRequest(BaseModel):
    patient_id: str = Field(..., min_length=1, description="Non-empty patient identifier.")
    consultation: str = Field(..., min_length=1, description="Non-empty clinician consultation notes.")


@router.post("/context", status_code=status.HTTP_200_OK)
async def doctor_context_assistance(payload: DoctorContextRequest):
    """
    Day 12 Doctor-Side Context Assistance Endpoint.

    Retrieves active current patient profile and longitudinal history from MongoDB,
    synthesizes it with the current consultation notes, and returns structured doctor assistance.

    Prototype Note: Unauthenticated prototype endpoint for clinical research decision support.
    """
    if not payload.patient_id or not payload.patient_id.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="patient_id must be a non-empty string."
        )
    if not payload.consultation or not payload.consultation.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="consultation must be a non-empty string."
        )

    try:
        result = doctor_context_service.generate_doctor_assistance(
            patient_id=payload.patient_id,
            consultation=payload.consultation
        )
        result["disclaimer"] = (
            "This system provides patient-reported context support for clinician review. "
            "Clinical diagnosis, prescribing, and medical decisions remain the sole responsibility of the treating clinician."
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        logger.error(f"Doctor context assistance endpoint error for patient '{payload.patient_id}': {e}", exc_info=True)
        # Controlled server response without leaking DB credentials or stack traces
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating doctor context assistance."
        )


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
        "message": "Doctor context retrieval logic active via /api/doctor/context."
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
        "reply": f"[Doctor AI Placeholder] Answering doctor query for patient {payload.patient_id}.",
        "disclaimer": "The final medical decision always belongs to the doctor."
    }

