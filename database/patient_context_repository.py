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
from bson import ObjectId
from bson.errors import InvalidId
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

    def __init__(self, collection: Optional[Any] = None):
        self._collection = collection

    def _get_coll(self) -> Any:
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
        Attaches `patient_id`, UTC `captured_at`, and default `is_current=True` metadata.
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

        # Attach database metadata (Day 11 longitudinal additions)
        doc["patient_id"] = patient_id
        doc["captured_at"] = datetime.now(timezone.utc)
        doc["is_current"] = True

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
        Retrieves all stored context records for a given patient_id (full history).
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

    def get_current_patient_context(
        self, patient_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves active/current context records for a given patient_id.
        Matches records where `is_current == True` or `is_current` is missing (legacy records).
        Ordered deterministically from oldest to newest by `captured_at`.

        Returns records with `_id` converted to string format.
        """
        clean_patient_id = self._validate_patient_id(patient_id)
        coll = self._get_coll()

        try:
            query = {
                "patient_id": clean_patient_id,
                "$or": [{"is_current": True}, {"is_current": {"$exists": False}}]
            }
            cursor = coll.find(query).sort("captured_at", ASCENDING)
            records = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                records.append(doc)
            return records
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed during get_current_patient_context: {e}") from e

    def get_current_context_candidates(
        self, patient_id: str, source: str, category: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves active/current records matching patient_id, source, and category.
        Used to form the minimal candidate set for longitudinal deduplication / update classification.
        """
        clean_patient_id = self._validate_patient_id(patient_id)
        coll = self._get_coll()

        try:
            query = {
                "patient_id": clean_patient_id,
                "source": source,
                "category": category,
                "$or": [{"is_current": True}, {"is_current": {"$exists": False}}]
            }
            cursor = coll.find(query).sort("captured_at", ASCENDING)
            records = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                records.append(doc)
            return records
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed during get_current_context_candidates: {e}") from e

    def mark_context_superseded(
        self,
        old_id: str,
        new_id: str,
        superseded_at: Optional[datetime] = None,
        patient_id: Optional[str] = None,
    ) -> bool:
        """
        Marks an existing context document as superseded by a newer record.

        Sets:
        - `is_current = False`
        - `superseded_at = superseded_at or UTC now`
        - `superseded_by = new_id`

        Returns True if successful, False if document was not found or update failed.
        Never leaks raw ObjectId types or raw stack traces.
        """
        if not old_id or not isinstance(old_id, str):
            return False
        if not new_id or not isinstance(new_id, str):
            return False

        coll = self._get_coll()
        now_utc = superseded_at if superseded_at is not None else datetime.now(timezone.utc)

        # Build query for single document matching old_id (support both ObjectId and string _id for mocks)
        query: Dict[str, Any] = {}
        try:
            query["_id"] = ObjectId(old_id)
        except (InvalidId, TypeError):
            # Fallback for string _id (e.g. in mock environments)
            query["_id"] = old_id

        if patient_id and isinstance(patient_id, str) and patient_id.strip():
            query["patient_id"] = patient_id.strip()

        update_doc = {
            "$set": {
                "is_current": False,
                "superseded_at": now_utc,
                "superseded_by": new_id,
            }
        }

        try:
            result = coll.update_one(query, update_doc)
            return result.modified_count > 0 or result.matched_count > 0
        except PyMongoError as e:
            raise RuntimeError(f"Database operation failed during mark_context_superseded: {e}") from e

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


def get_current_patient_context(patient_id: str) -> List[Dict[str, Any]]:
    """Convenience wrapper for retrieving active patient context profile."""
    return _repository.get_current_patient_context(patient_id)


def get_current_context_candidates(patient_id: str, source: str, category: str) -> List[Dict[str, Any]]:
    """Convenience wrapper for retrieving active context candidates."""
    return _repository.get_current_context_candidates(patient_id, source, category)


def mark_context_superseded(
    old_id: str, new_id: str, superseded_at: Optional[datetime] = None, patient_id: Optional[str] = None
) -> bool:
    """Convenience wrapper for marking a record as superseded."""
    return _repository.mark_context_superseded(old_id, new_id, superseded_at, patient_id)


def delete_patient_context(patient_id: str) -> int:
    """Convenience wrapper for deleting patient context records."""
    return _repository.delete_patient_context(patient_id)
