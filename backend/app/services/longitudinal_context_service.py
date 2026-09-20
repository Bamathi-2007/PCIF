"""
PCIF Longitudinal Context Service.

Orchestrates database-level longitudinal consolidation for CCEE-extracted ClinicalContextItem objects.

Core Responsibilities:
1. Prevents repeated chat processing from accumulating redundant duplicate records.
2. Classifies relationships to active current records into: DUPLICATE, UPDATE, or DISTINCT.
3. Fast path: Deterministic exact/normalized duplicate check without Gemini call.
4. Safeguard: Poorer representation never replaces a richer active context record.
5. Fail-safe update order: Inserts new record FIRST before superseding old record.
6. Preserves immutable longitudinal history via `is_current`, `superseded_at`, and `superseded_by` database metadata.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from ccee.schema import ClinicalContextItem
from database.patient_context_repository import PatientContextRepository, _repository
from backend.app.services.llm_service import GeminiLLMService, llm_service

logger = logging.getLogger(__name__)


@dataclass
class LongitudinalPersistenceResult:
    """Dataclass encapsulating result counts of longitudinal context persistence."""
    inserted_count: int = 0
    duplicate_count: int = 0
    superseded_count: int = 0
    failed_count: int = 0


def normalize_str(val: Optional[str]) -> str:
    """Helper to normalize text for deterministic comparison: trim, lowercase, collapse spaces."""
    if val is None:
        return ""
    return " ".join(val.strip().lower().split())


def is_exact_normalized_duplicate(cand: Dict[str, Any], item_dict: Dict[str, Any]) -> bool:
    """
    Fast path deterministic check for exact normalized duplication across core schema fields.
    """
    fields = ["category", "summary", "source", "record_type", "value", "duration"]
    for field in fields:
        if normalize_str(cand.get(field)) != normalize_str(item_dict.get(field)):
            return False
    return True


def is_poorer_duplicate(cand: Dict[str, Any], item_dict: Dict[str, Any]) -> bool:
    """
    Safeguard check: Returns True if the new item is a poorer representation of an existing candidate.
    (e.g., candidate has duration/detail while new item matches summary/value but lacks duration).
    """
    if normalize_str(cand.get("category")) != normalize_str(item_dict.get("category")):
        return False
    if normalize_str(cand.get("summary")) != normalize_str(item_dict.get("summary")):
        return False
    if normalize_str(cand.get("value")) != normalize_str(item_dict.get("value")):
        return False
    # If candidate has duration info but new item lacks duration info
    if cand.get("duration") and not item_dict.get("duration"):
        return True
    return False


class LongitudinalContextService:
    """
    Service for managing database-level longitudinal consolidation of patient context.
    """

    def __init__(
        self,
        repository: Optional[PatientContextRepository] = None,
        llm: Optional[GeminiLLMService] = None,
    ):
        self._repository = repository or _repository
        self._llm = llm or llm_service

    def save_longitudinal_context(
        self, patient_id: str, items: List[ClinicalContextItem]
    ) -> LongitudinalPersistenceResult:
        """
        Consolidates and persists a list of ClinicalContextItem objects for a patient.

        For each item:
        1. Retrieves active candidate records matching patient_id, source, and category.
        2. Applies deterministic fast-path exact duplicate check.
        3. Applies poorer-duplicate safeguard check.
        4. If required, invokes LLM semantic relation classifier.
        5. Executes appropriate DUPLICATE / UPDATE / DISTINCT persistence.
        """
        result = LongitudinalPersistenceResult()

        if not items:
            return result

        clean_patient_id = patient_id.strip()

        for item in items:
            try:
                self._process_single_item(clean_patient_id, item, result)
            except Exception as e:
                logger.error(
                    f"Error processing longitudinal item for patient '{clean_patient_id}': {e}",
                    exc_info=True,
                )
                result.failed_count += 1

        return result

    def _process_single_item(
        self,
        patient_id: str,
        item: ClinicalContextItem,
        result: LongitudinalPersistenceResult,
    ) -> None:
        item_dict = item.to_dict()

        # Step 1: Retrieve candidate active records (same patient, source, category, current=True)
        candidates = self._repository.get_current_context_candidates(
            patient_id=patient_id,
            source=item.source,
            category=item.category,
        )

        if not candidates:
            # No existing active candidates: insert as distinct new record
            self._repository.save_context_item(patient_id, item)
            result.inserted_count += 1
            return

        # Step 2: Deterministic Fast Path (Exact normalized duplicate check)
        for cand in candidates:
            if is_exact_normalized_duplicate(cand, item_dict):
                logger.info(f"Fast-path exact duplicate detected for patient '{patient_id}', skipping insert.")
                result.duplicate_count += 1
                return

        # Step 3: Safeguard against replacing rich context with poorer representation
        for cand in candidates:
            if is_poorer_duplicate(cand, item_dict):
                logger.info(f"Poorer representation detected for existing rich record, skipping insert as DUPLICATE.")
                result.duplicate_count += 1
                return

        # Step 4: Semantic Relation Classification via LLM
        matched_action = None
        target_candidate = None

        for cand in candidates:
            try:
                rel = self._llm.classify_longitudinal_relation(cand, item_dict)
            except Exception as e:
                logger.warning(
                    f"Classifier call raised exception '{e}'; falling back safely to 'distinct'."
                )
                rel = "distinct"

            if rel == "duplicate":
                matched_action = "duplicate"
                target_candidate = cand
                break
            elif rel == "update":
                matched_action = "update"
                target_candidate = cand
                break
            # If "distinct", continue checking next candidate

        # Step 5: Execute persistence action
        if matched_action == "duplicate":
            result.duplicate_count += 1
            return

        elif matched_action == "update" and target_candidate:
            # FAIL-SAFE UPDATE SEQUENCE:
            # 1. Insert NEW record first with is_current=True
            new_id = self._repository.save_context_item(patient_id, item)
            result.inserted_count += 1

            # 2. Only after successful insertion, mark old candidate as superseded
            try:
                supersede_ok = self._repository.mark_context_superseded(
                    old_id=target_candidate["_id"],
                    new_id=new_id,
                    patient_id=patient_id,
                )
                if supersede_ok:
                    result.superseded_count += 1
                else:
                    logger.warning(
                        f"Supersede update returned False for old record '{target_candidate['_id']}'; both remain current."
                    )
            except Exception as se:
                logger.error(
                    f"Fail-safe warning: Failed to mark old record '{target_candidate['_id']}' superseded: {se}. Both records remain active."
                )
            return

        else:
            # Action is "distinct" (or fallback)
            self._repository.save_context_item(patient_id, item)
            result.inserted_count += 1
            return


# Module singleton instance
longitudinal_context_service = LongitudinalContextService()
