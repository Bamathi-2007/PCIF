import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.app.services.doctor_context_service import doctor_context_service
from database.doctor_notes_repository import save_doctor_note, get_doctor_notes

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/doctor", tags=["Doctor Assistant"])


class SaveDoctorNoteRequest(BaseModel):
    patient_id: str = Field(..., description="Non-empty patient identifier.")
    note: str = Field(..., description="Non-empty clinician-authored note.")


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


@router.post("/notes", status_code=status.HTTP_200_OK)
async def save_clinician_note(payload: SaveDoctorNoteRequest):
    """
    Day 14 Clinician-Authored Note Persistence Endpoint.

    Saves explicitly clinician-authored notes into the isolated `doctor_notes` collection.
    Server strictly controls record_type = 'doctor_confirmed' and created_at.
    Does NOT pass through CCEE or Day 11 consolidation.
    """
    if not payload.patient_id or not payload.patient_id.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="patient_id must be a non-empty string."
        )
    if not payload.note or not payload.note.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="note must be a non-empty string."
        )

    try:
        saved = save_doctor_note(payload.patient_id.strip(), payload.note.strip())
        created_at_val = saved.get("created_at")
        if isinstance(created_at_val, datetime):
            created_at_str = created_at_val.isoformat()
        else:
            created_at_str = str(created_at_val) if created_at_val else ""

        return {
            "status": "saved",
            "note": {
                "id": str(saved.get("id") or saved.get("_id")),
                "patient_id": saved.get("patient_id"),
                "note": saved.get("note"),
                "record_type": "doctor_confirmed",
                "created_at": created_at_str,
            }
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to save doctor note for patient '{payload.patient_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the doctor note."
        )


@router.get("/notes/{patient_id}", status_code=status.HTTP_200_OK)
async def get_clinician_notes(patient_id: str):
    """
    Day 14 Clinician-Authored Note Retrieval Endpoint.

    Retrieves all explicitly clinician-authored notes stored in `doctor_notes` collection for a patient.
    Ordered newest-first. Never returns raw BSON ObjectIds.
    """
    if not patient_id or not patient_id.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="patient_id must be a non-empty string."
        )

    try:
        raw_notes = get_doctor_notes(patient_id.strip())
        formatted_notes = []
        for n in raw_notes:
            created_at_val = n.get("created_at")
            if isinstance(created_at_val, datetime):
                created_at_str = created_at_val.isoformat()
            else:
                created_at_str = str(created_at_val) if created_at_val else ""

            formatted_notes.append({
                "id": str(n.get("id") or n.get("_id")),
                "patient_id": n.get("patient_id", patient_id.strip()),
                "note": n.get("note", ""),
                "record_type": n.get("record_type", "doctor_confirmed"),
                "created_at": created_at_str,
            })

        return {
            "patient_id": patient_id.strip(),
            "notes": formatted_notes,
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to retrieve doctor notes for patient '{patient_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving doctor notes."
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


