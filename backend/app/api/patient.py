"""
Patient Management Route Placeholders.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/patient", tags=["Patient"])


@router.get("/profile/{patient_id}")
async def get_patient_profile(patient_id: str):
    """Retrieve patient profile overview placeholder."""
    return {
        "patient_id": patient_id,
        "name": "Demo Patient",
        "age": 34,
        "status": "Placeholder (Day 1)"
    }


@router.get("/history/{patient_id}")
async def get_patient_history(patient_id: str):
    """Retrieve combined longitudinal history for patient placeholder."""
    return {
        "patient_id": patient_id,
        "longitudinal_context": [],
        "status": "Placeholder (Day 1)"
    }
