"""
Database Integration Package for PCIF.
Manages MongoDB connections, collections, and patient context persistence.
"""

from database.mongodb import (
    MongoDBManager,
    db_manager,
    get_database,
    get_patient_context_collection,
    ping_database,
)
from database.patient_context_repository import (
    PatientContextRepository,
    save_context_item,
    save_context_items,
    get_patient_context,
    delete_patient_context,
)

__all__ = [
    "MongoDBManager",
    "db_manager",
    "get_database",
    "get_patient_context_collection",
    "ping_database",
    "PatientContextRepository",
    "save_context_item",
    "save_context_items",
    "get_patient_context",
    "delete_patient_context",
]
