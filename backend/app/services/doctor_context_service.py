"""
PCIF Doctor Context Service.

Orchestrates context retrieval and contextual assistance generation for clinician consultation workflows.

Key Responsibilities:
1. Validates patient_id and consultation inputs.
2. Retrieves active current profile (`get_current_patient_context`).
3. Retrieves longitudinal context history (`get_patient_context`) capped at deterministic limit (max 20 records).
4. Retrieves clinician-authored notes history (`get_doctor_notes`) capped at deterministic limit (max 10 notes).
5. Cleans internal database metadata (_id, superseded_by).
6. Handles empty patient history cleanly without fabrication or failure across all three provenance channels.
7. Invokes Gemini LLM Service with DOCTOR_CONTEXT_SYSTEM_INSTRUCTION.
8. Does NOT persist doctor consultation or Doctor AI output (transient read + assist only).
"""

import logging
from typing import Dict, Any, List, Optional

from database.patient_context_repository import (
    PatientContextRepository,
    _repository,
    get_current_patient_context,
    get_patient_context,
)
from database.doctor_notes_repository import (
    DoctorNotesRepository,
    _doctor_notes_repository,
    get_doctor_notes,
)
from backend.app.services.llm_service import GeminiLLMService, llm_service

logger = logging.getLogger(__name__)

# Maximum deterministic history limits to prevent prompt overflow
MAX_HISTORY_LIMIT = 20
MAX_CLINICIAN_NOTES = 10


class DoctorContextService:
    """
    Service responsible for Doctor-Side Context Assistance generation.
    """

    def __init__(
        self,
        repository: Optional[PatientContextRepository] = None,
        doctor_notes_repo: Optional[DoctorNotesRepository] = None,
        llm: Optional[GeminiLLMService] = None,
    ):
        self._repository = repository or _repository
        self._doctor_notes_repo = doctor_notes_repo or _doctor_notes_repository
        self._llm = llm or llm_service

    @staticmethod
    def _validate_input(patient_id: str, consultation: str) -> tuple[str, str]:
        if not patient_id or not isinstance(patient_id, str) or not patient_id.strip():
            raise ValueError("patient_id must be a non-empty string.")
        if not consultation or not isinstance(consultation, str) or not consultation.strip():
            raise ValueError("consultation must be a non-empty string.")
        return patient_id.strip(), consultation.strip()

    def generate_doctor_assistance(
        self, patient_id: str, consultation: str
    ) -> Dict[str, Any]:
        """
        Retrieves patient context and clinician notes, generating concise doctor-facing assistance.

        Args:
            patient_id (str): Application patient identifier.
            consultation (str): Current clinician consultation notes.

        Returns:
            Dict[str, Any]: Structured doctor response containing patient_id and assistant object.
        """
        clean_patient_id, clean_consultation = self._validate_input(patient_id, consultation)

        # 1. Retrieve active current context profile
        try:
            current_context = self._repository.get_current_patient_context(clean_patient_id)
        except Exception as e:
            logger.error(f"Error retrieving current patient context for doctor assist '{clean_patient_id}': {e}")
            raise RuntimeError(f"Database context retrieval failed: {e}") from e

        # 2. Retrieve longitudinal context history
        try:
            full_history = self._repository.get_patient_context(clean_patient_id)
        except Exception as e:
            logger.error(f"Error retrieving longitudinal history for doctor assist '{clean_patient_id}': {e}")
            raise RuntimeError(f"Database context retrieval failed: {e}") from e

        # 3. Retrieve clinician-authored notes
        try:
            doctor_notes = self._doctor_notes_repo.get_doctor_notes(clean_patient_id)
        except Exception as e:
            logger.error(f"Error retrieving doctor notes for doctor assist '{clean_patient_id}': {e}")
            raise RuntimeError(f"Database clinician notes retrieval failed: {e}") from e

        # 4. Apply deterministic history limits
        limited_history = full_history[-MAX_HISTORY_LIMIT:] if len(full_history) > MAX_HISTORY_LIMIT else full_history
        limited_clinician_notes = doctor_notes[:MAX_CLINICIAN_NOTES] if len(doctor_notes) > MAX_CLINICIAN_NOTES else doctor_notes

        # 5. Generate structured Doctor AI response across three provenance channels
        assistant_output = self._llm.generate_doctor_context_assistance(
            patient_id=clean_patient_id,
            consultation=clean_consultation,
            current_context=current_context,
            longitudinal_history=limited_history,
            clinician_notes=limited_clinician_notes,
        )

        # Handle empty history explicitly if LLM produced empty summary
        if (
            not current_context
            and not full_history
            and not limited_clinician_notes
            and not assistant_output.get("context_summary")
        ):
            assistant_output["context_summary"] = (
                "No prior structured patient context or clinician notes are available for this patient."
            )

        return {
            "patient_id": clean_patient_id,
            "assistant": assistant_output,
        }


# Module singleton instance
doctor_context_service = DoctorContextService()

