"""
Patient Context Repository for PCIF.

Provides persistence and retrieval mechanisms for CCEE-extracted ClinicalContextItem objects
stored in the `patient_context` collection in MongoDB.

Core Privacy Enforcement:
PCIF stores ONLY validated CCEE context items. Raw conversation transcripts, Gemini prompt/responses,
or chat history objects are strictly prohibited from database persistence.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from ccee.schema import ClinicalContextItem
from database.mongodb import get_patient_context_collection

# Forbidden fields that must NEVER be persisted in patient context database
FORBIDDEN_PRIVACY_KEYS = {
    "conversation",
    "messages",
    "history",
    "raw_text",
    "assistant_response",
    "prompt",
    "system_instruction",
    "transcript",
    "chat_history",
}


class PatientContextRepository:
    """
    Repository for managing patient context persistence in MongoDB.
    """

    def __init__(self, collection: Optional[Collection] = None):
        self._collection = collection

    def _get_coll(self) -> Collection:
        if self._collection is not None:
            return self._collection
        return get_patient_context_collection()

    @staticmethod
    def _validate_patient_id(patient_id: str) -> str:
        if not patient_id or not isinstance(patient_id, str) or not patient_id.strip():
            raise ValueError("patient_id must be a non-empty string.")
        return patient_id.strip()

    @staticmethod
    def prepare_document(patient_id: str, item: ClinicalContextItem) -> Dict[str, Any]:
        """
        Converts a ClinicalContextItem into a database document dictionary.
        Attaches `patient_id` and UTC `captured_at` metadata.
        Strictly enforces privacy by excluding forbidden raw conversation fields.
        """
        if not isinstance(item, ClinicalContextItem):
            raise ValueError(f"Expected ClinicalContextItem instance, got {type(item).__name__}.")

        # Convert item to dict using frozen schema method (excludes None optional fields)
        doc = item.to_dict()

        # Enforce Privacy Principle: Reject any document containing forbidden raw text keys
        for key in FORBIDDEN_PRIVACY_KEYS:
            if key in doc:
                raise ValueError(f"Privacy Violation: Forbidden raw conversation key '{key}' present in document.")

        # Attach database metadata
        doc["patient_id"] = patient_id
        doc["captured_at"] = datetime.now(timezone.utc)

        return doc

    def save_context_items(
        self, patient_id: str, items: List[ClinicalContextItem]
    ) -> List[str]:
        """
        Persists a list of ClinicalContextItem objects under the given patient_id.

        Requirements:
        - Rejects empty/blank patient_id.
        - Returns [] if items list is empty without performing DB operations.
        - Preserves source and record_type exactly.
        - Never mutates original ClinicalContextItem instances.
        - Returns list of inserted MongoDB string IDs.
        """
        clean_patient_id = self._validate_patient_id(patient_id)

        if not items:
            return []

        coll = self._get_coll()
        documents = [self.prepare_document(clean_patient_id, item) for item in items]

        try:
            result = coll.insert_many(documents)
            return [str(inserted_id) for inserted_id in result.inserted_ids]
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed during save_context_items: {e}") from e

    def save_context_item(
        self, patient_id: str, item: ClinicalContextItem
    ) -> str:
        """
        Persists a single ClinicalContextItem under the given patient_id.
        Returns the inserted document string ID.
        """
        inserted_ids = self.save_context_items(patient_id, [item])
        return inserted_ids[0]

    def get_patient_context(
        self, patient_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all stored context records for a given patient_id.
        Records are ordered deterministically from oldest to newest by `captured_at`.

        Returns records with `_id` converted to string format.
        """
        clean_patient_id = self._validate_patient_id(patient_id)
        coll = self._get_coll()

        try:
            cursor = coll.find({"patient_id": clean_patient_id}).sort("captured_at", ASCENDING)
            records = []
            for doc in cursor:
                # Convert ObjectId to string for clean domain representation
                doc["_id"] = str(doc["_id"])
                records.append(doc)
            return records
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed during get_patient_context: {e}") from e

    def delete_patient_context(
        self, patient_id: str
    ) -> int:
        """
        Deletes all stored context records for a given patient_id.
        Mainly used for test cleanup and isolation testing.
        Returns count of deleted documents.
        """
        clean_patient_id = self._validate_patient_id(patient_id)
        coll = self._get_coll()

        try:
            result = coll.delete_many({"patient_id": clean_patient_id})
            return result.deleted_count
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed during delete_patient_context: {e}") from e


# Convenience module-level instances and wrapper functions
_repository = PatientContextRepository()


def save_context_item(patient_id: str, item: ClinicalContextItem) -> str:
    """Convenience wrapper for saving a single context item."""
    return _repository.save_context_item(patient_id, item)


def save_context_items(patient_id: str, items: List[ClinicalContextItem]) -> List[str]:
    """Convenience wrapper for saving multiple context items."""
    return _repository.save_context_items(patient_id, items)


def get_patient_context(patient_id: str) -> List[Dict[str, Any]]:
    """Convenience wrapper for retrieving patient context history."""
    return _repository.get_patient_context(patient_id)


def delete_patient_context(patient_id: str) -> int:
    """Convenience wrapper for deleting patient context records."""
    return _repository.delete_patient_context(patient_id)
