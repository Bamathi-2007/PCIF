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

logger = logging.getLogger(__name__)


@dataclass
class ContextPersistenceResult:
    """Dataclass encapsulating context extraction & database persistence result."""
    status: str  # "saved", "no_relevant_context", "failed"
    saved_count: int = 0


class ContextPersistenceService:
    """
    Service responsible for orchestrating CCEE extraction and MongoDB persistence.
    """

    def __init__(
        self,
        ccee: Optional[ClinicalContextExtractionEngine] = None,
        repository: Optional[PatientContextRepository] = None
    ):
        self._ccee = ccee or ccee_engine
        self._repository = repository or _repository

    def extract_and_persist_context(
        self,
        patient_id: str,
        conversation: Union[str, List[Dict[str, Any]]],
        source: str
    ) -> ContextPersistenceResult:
        """
        Extracts clinical context items from the active conversation using CCEE,
        validates the output, and persists valid items to MongoDB.

        Args:
            patient_id (str): Explicit, non-empty patient identifier.
            conversation (Union[str, List[Dict[str, Any]]]): Role-aware turn dicts or formatted text.
            source (str): Source AI module ('nutrition' or 'mental_wellness').

        Returns:
            ContextPersistenceResult: Result object containing status and saved_count.
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

        # Step 3: Persist extracted ClinicalContextItem instances to MongoDB
        try:
            inserted_ids = self._repository.save_context_items(
                patient_id=clean_patient_id,
                items=items
            )
            return ContextPersistenceResult(
                status="saved",
                saved_count=len(inserted_ids)
            )
        except Exception as e:
            logger.error(
                f"Context persistence failed during database insert for patient '{clean_patient_id}': {e}",
                exc_info=True
            )
            return ContextPersistenceResult(status="failed", saved_count=0)


# Module singleton instance
context_persistence_service = ContextPersistenceService()
