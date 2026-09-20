"""
PCIF Context Persistence Service.

Orchestrates the extraction of clinical context from patient conversations via CCEE
and persists validated ClinicalContextItem objects to MongoDB using PatientContextRepository.

Key Principles:
- NEVER persists raw chat history, user messages, assistant responses, or prompts.
- Distinguishes three persistence outcomes: 'saved', 'no_relevant_context', and 'failed'.
- Fail-safe exception handling ensuring chat availability even during CCEE/DB failures.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Union, Optional

from ccee.engine import ccee_engine, ClinicalContextExtractionEngine
from database.patient_context_repository import PatientContextRepository, _repository
from backend.app.services.longitudinal_context_service import (
    LongitudinalContextService,
    longitudinal_context_service,
)

logger = logging.getLogger(__name__)


@dataclass
class ContextPersistenceResult:
    """Dataclass encapsulating context extraction & database persistence result."""
    status: str  # "saved", "no_relevant_context", "failed"
    saved_count: int = 0
    duplicate_count: int = 0
    superseded_count: int = 0


class ContextPersistenceService:
    """
    Service responsible for orchestrating CCEE extraction and MongoDB longitudinal persistence.
    """

    def __init__(
        self,
        ccee: Optional[ClinicalContextExtractionEngine] = None,
        repository: Optional[PatientContextRepository] = None,
        longitudinal_service: Optional[LongitudinalContextService] = None,
    ):
        self._ccee = ccee or ccee_engine
        self._repository = repository or _repository
        self._longitudinal_service = longitudinal_service or longitudinal_context_service

    def extract_and_persist_context(
        self,
        patient_id: str,
        conversation: Union[str, List[Dict[str, Any]]],
        source: str
    ) -> ContextPersistenceResult:
        """
        Extracts clinical context items from the active conversation using CCEE,
        validates the output, and applies longitudinal consolidation before persisting to MongoDB.

        Args:
            patient_id (str): Explicit, non-empty patient identifier.
            conversation (Union[str, List[Dict[str, Any]]]): Role-aware turn dicts or formatted text.
            source (str): Source AI module ('nutrition' or 'mental_wellness').

        Returns:
            ContextPersistenceResult: Result object containing status and count metadata.
        """
        if not patient_id or not isinstance(patient_id, str) or not patient_id.strip():
            logger.error("Context persistence attempted with empty or missing patient_id.")
            return ContextPersistenceResult(status="failed", saved_count=0)

        clean_patient_id = patient_id.strip()

        # Step 1: Execute CCEE extraction
        try:
            items = self._ccee.extract_context(
                conversation=conversation,
                source=source
            )
        except Exception as e:
            logger.error(
                f"Context persistence failed during CCEE extraction for patient '{clean_patient_id}': {e}",
                exc_info=True
            )
            return ContextPersistenceResult(status="failed", saved_count=0)

        # Step 2: Handle empty extraction (normal success with no clinical facts)
        if not items:
            return ContextPersistenceResult(status="no_relevant_context", saved_count=0)

        # Step 3: Apply longitudinal consolidation & persistence
        try:
            long_res = self._longitudinal_service.save_longitudinal_context(
                patient_id=clean_patient_id,
                items=items
            )

            # Determine response status
            if long_res.inserted_count > 0 or long_res.duplicate_count > 0:
                status = "saved"
            elif long_res.failed_count > 0 and long_res.inserted_count == 0:
                status = "failed"
            else:
                status = "saved"

            return ContextPersistenceResult(
                status=status,
                saved_count=long_res.inserted_count,
                duplicate_count=long_res.duplicate_count,
                superseded_count=long_res.superseded_count,
            )
        except Exception as e:
            logger.error(
                f"Context persistence failed during longitudinal processing for patient '{clean_patient_id}': {e}",
                exc_info=True
            )
            return ContextPersistenceResult(status="failed", saved_count=0)


# Module singleton instance
context_persistence_service = ContextPersistenceService()
