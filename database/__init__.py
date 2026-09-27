"""
Database Integration Package for PCIF.
Manages MongoDB connections, collections, and patient context persistence.
"""

from database.mongodb import (
    MongoDBManager,
    db_manager,
    get_database,
    get_patient_context_collection,
    get_doctor_notes_collection,
    ping_database,
)
from database.patient_context_repository import (
    PatientContextRepository,
    save_context_item,
    save_context_items,
    get_patient_context,
    get_current_patient_context,
    get_current_context_candidates,
    mark_context_superseded,
    delete_patient_context,
)
from database.doctor_notes_repository import (
    DoctorNotesRepository,
    save_doctor_note,
    get_doctor_notes,
    delete_doctor_notes,
)

__all__ = [
    "MongoDBManager",
    "db_manager",
    "get_database",
    "get_patient_context_collection",
    "get_doctor_notes_collection",
    "ping_database",
    "PatientContextRepository",
    "save_context_item",
    "save_context_items",
    "get_patient_context",
    "get_current_patient_context",
    "get_current_context_candidates",
    "mark_context_superseded",
    "delete_patient_context",
    "DoctorNotesRepository",
    "save_doctor_note",
    "get_doctor_notes",
    "delete_doctor_notes",
]

