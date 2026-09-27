"""
Doctor Notes Repository for PCIF.

Provides explicit clinician-authored note persistence and retrieval using
the isolated `doctor_notes` collection in MongoDB.

Core Trust Boundary & Provenance:
- Source: Explicitly clinician-authored text only.
- Record Type: `doctor_confirmed` (strictly server-controlled).
- Stored in a separate collection from `patient_context` (which holds `patient_reported` CCEE items).
- Doctor notes NEVER pass through CCEE or Day 11 longitudinal consolidation.
- Append-only: all explicitly saved clinician notes are preserved without overwriting or superseding.
- created_at indicates database persistence timestamp only (not symptom onset, diagnosis date, or visit date).
- Prototype limitation: The current prototype does not verify clinician identity or authorize access to patient records.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from bson import ObjectId
from pymongo import DESCENDING
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from database.mongodb import get_doctor_notes_collection

# Forbidden fields that must never be persisted in doctor notes
FORBIDDEN_PRIVACY_KEYS = {
    "conversation",
    "messages",
    "history",
    "raw_chat",
    "raw_text",
    "assistant_response",
    "prompt",
    "system_instruction",
    "transcript",
    "chat_history",
}


class DoctorNotesRepository:
    """
    Repository for managing clinician-authored note persistence in MongoDB.
    """

    def __init__(self, collection: Optional[Any] = None):
        self._collection = collection

    def _get_coll(self) -> Any:
        if self._collection is not None:
            return self._collection
        return get_doctor_notes_collection()

    @staticmethod
    def _validate_patient_id(patient_id: str) -> str:
        if not patient_id or not isinstance(patient_id, str) or not patient_id.strip():
            raise ValueError("patient_id must be a non-empty string.")
        return patient_id.strip()

    @staticmethod
    def _validate_note(note: str) -> str:
        if not note or not isinstance(note, str) or not note.strip():
            raise ValueError("note must be a non-empty string.")
        return note.strip()

    def save_doctor_note(self, patient_id: str, note: str) -> Dict[str, Any]:
        """
        Persists an explicitly clinician-authored note under the given patient_id.

        Server strictly controls:
        - `record_type = "doctor_confirmed"` (caller cannot override)
        - `created_at = datetime.now(timezone.utc)` (persistence timestamp only)

        Requirements:
        - Rejects empty/whitespace-only patient_id or note.
        - Stores in `doctor_notes` collection (never `patient_context`).
        - Does NOT pass through CCEE or Day 11 consolidation.
        - Append-only: preserves all saved notes.
        - Returns structured note dictionary with string ID.
        """
        clean_patient_id = self._validate_patient_id(patient_id)
        clean_note = self._validate_note(note)

        coll = self._get_coll()
        now_utc = datetime.now(timezone.utc)

        doc: Dict[str, Any] = {
            "patient_id": clean_patient_id,
            "note": clean_note,
            "record_type": "doctor_confirmed",
            "created_at": now_utc,
        }

        try:
            result = coll.insert_one(doc)
            inserted_id_str = str(result.inserted_id)
            return {
                "id": inserted_id_str,
                "_id": inserted_id_str,
                "patient_id": clean_patient_id,
                "note": clean_note,
                "record_type": "doctor_confirmed",
                "created_at": now_utc,
            }
        except (PyMongoError, Exception) as e:
            raise RuntimeError(f"Database operation failed during save_doctor_note: {e}") from e

    def get_doctor_notes(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all clinician-authored notes for a given patient_id.
        Notes are ordered newest-first by `created_at` DESCENDING.

        Never returns raw BSON ObjectIds (converts `_id` to string `id`).
        """
        clean_patient_id = self._validate_patient_id(patient_id)
        coll = self._get_coll()

        try:
            cursor = coll.find({"patient_id": clean_patient_id}).sort("created_at", DESCENDING)
            notes = []
            for doc in cursor:
                doc_id_str = str(doc["_id"])
                notes.append({
                    "id": doc_id_str,
                    "_id": doc_id_str,
                    "patient_id": doc.get("patient_id", clean_patient_id),
                    "note": doc.get("note", ""),
                    "record_type": doc.get("record_type", "doctor_confirmed"),
                    "created_at": doc.get("created_at"),
                })
            return notes
        except (PyMongoError, Exception) as e:
            raise RuntimeError(f"Database operation failed during get_doctor_notes: {e}") from e

    def delete_doctor_notes(self, patient_id: str) -> int:
        """
        Deletes all stored doctor notes for a given patient_id.
        Used for test isolation and cleanup.
        Returns count of deleted documents.
        """
        clean_patient_id = self._validate_patient_id(patient_id)
        coll = self._get_coll()

        try:
            result = coll.delete_many({"patient_id": clean_patient_id})
            return result.deleted_count
        except (PyMongoError, Exception) as e:
            raise RuntimeError(f"Database operation failed during delete_doctor_notes: {e}") from e



# Convenience module-level instance and wrapper functions
_doctor_notes_repository = DoctorNotesRepository()


def save_doctor_note(patient_id: str, note: str) -> Dict[str, Any]:
    """Convenience wrapper for saving a clinician-authored note."""
    return _doctor_notes_repository.save_doctor_note(patient_id, note)


def get_doctor_notes(patient_id: str) -> List[Dict[str, Any]]:
    """Convenience wrapper for retrieving clinician-authored notes."""
    return _doctor_notes_repository.get_doctor_notes(patient_id)


def delete_doctor_notes(patient_id: str) -> int:
    """Convenience wrapper for deleting doctor notes."""
    return _doctor_notes_repository.delete_doctor_notes(patient_id)
