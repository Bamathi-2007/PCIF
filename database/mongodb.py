"""
MongoDB Database Connection & Management Layer for PCIF.

Manages connections to MongoDB using PyMongo, leveraging environment variables for configuration.
Requires explicit MONGODB_URI configuration without silent fallback to localhost.

Logical Collections:
1. `users` - Patient and Doctor account profiles (Future auth integration).
2. `patient_context` - Longitudinal context items extracted by CCEE or entered by clinician.
3. `doctor_notes` - Consultation records and confirmed clinical findings (Future doctor integration).
"""

import os
from datetime import timezone, datetime
from typing import Dict, Any, Optional
from pymongo import MongoClient, ASCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, ConnectionFailure, ServerSelectionTimeoutError

# Default collection names
COLLECTION_PATIENT_CONTEXT = "patient_context"
COLLECTION_USERS = "users"
COLLECTION_DOCTOR_NOTES = "doctor_notes"


class MongoDBManager:
    """
    Singleton connection manager for MongoDB.
    Supports environment-based configuration and fail-safe database access.
    Requires explicit MONGODB_URI configuration.
    """

    def __init__(self, uri: Optional[str] = None, db_name: Optional[str] = None):
        # Explicit URI selection: passed uri -> MONGODB_URI env var -> None (NO silent fallback to localhost)
        env_uri = os.getenv("MONGODB_URI")
        self._uri = uri if uri is not None else env_uri
        self._db_name = db_name if db_name is not None else os.getenv("MONGODB_DB_NAME", "pcif")
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        self._indexes_created = False

    @property
    def uri(self) -> Optional[str]:
        return self._uri

    @property
    def db_name(self) -> str:
        return self._db_name

    def get_client(self) -> MongoClient:
        """
        Returns or creates a shared MongoClient instance.
        Raises ConnectionError if MONGODB_URI is missing, blank, or invalid.
        """
        if self._client is None:
            if not self._uri or not isinstance(self._uri, str) or not self._uri.strip():
                raise ConnectionError(
                    "Configuration Error: MONGODB_URI is not configured or blank. Explicit MONGODB_URI is required."
                )
            try:
                # 5 second timeout for server selection during ping/operations
                self._client = MongoClient(self._uri, serverSelectionTimeoutMS=5000)
            except Exception as e:
                raise ConnectionError("Failed to initialize MongoClient with configured URI.") from e
        return self._client

    def get_database(self) -> Database:
        """
        Returns the PyMongo Database instance.
        """
        if self._db is None:
            client = self.get_client()
            self._db = client[self._db_name]
            self.ensure_indexes()
        return self._db

    def get_patient_context_collection(self) -> Collection:
        """
        Returns the `patient_context` collection instance.
        """
        db = self.get_database()
        return db[COLLECTION_PATIENT_CONTEXT]

    def ensure_indexes(self) -> None:
        """
        Ensures necessary indexes exist on collections.
        """
        if self._indexes_created or self._db is None:
            return
        try:
            patient_context_coll = self._db[COLLECTION_PATIENT_CONTEXT]
            # Index for patient queries
            patient_context_coll.create_index([("patient_id", ASCENDING)], background=True)
            # Compound index for timeline queries
            patient_context_coll.create_index(
                [("patient_id", ASCENDING), ("captured_at", ASCENDING)],
                background=True
            )
            # Compound index for active longitudinal context queries
            patient_context_coll.create_index(
                [("patient_id", ASCENDING), ("is_current", ASCENDING), ("captured_at", ASCENDING)],
                background=True
            )
            # Compound index for candidate lookup
            patient_context_coll.create_index(
                [("patient_id", ASCENDING), ("source", ASCENDING), ("category", ASCENDING)],
                background=True
            )
            self._indexes_created = True
        except Exception as e:
            # Safe index warning without exposing secrets
            print(f"[MongoDBManager] Warning: Index creation failed: {type(e).__name__}")

    def ping_database(self) -> bool:
        """
        Pings the database to verify live connectivity.
        Returns True if reachable, False otherwise. Does not expose secrets on error.
        """
        try:
            client = self.get_client()
            client.admin.command("ping")
            return True
        except Exception as e:
            # Log failure safely without exposing URI credentials
            print(f"[MongoDBManager] Database ping status: Unreachable ({type(e).__name__})")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Returns operational health status dictionary for monitoring.
        Does NOT expose sensitive URI credentials or stack traces.
        """
        is_alive = self.ping_database()
        return {
            "connected": is_alive,
            "db_name": self._db_name,
            "collections": [COLLECTION_USERS, COLLECTION_PATIENT_CONTEXT, COLLECTION_DOCTOR_NOTES],
            "status": "connected" if is_alive else "disconnected_or_unreachable"
        }

    def close(self) -> None:
        """Closes the MongoDB client connection if open."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            self._indexes_created = False


# Global lazy singleton instance
db_manager = MongoDBManager()


def get_database() -> Database:
    """Convenience getter for global database instance."""
    return db_manager.get_database()


def get_patient_context_collection() -> Collection:
    """Convenience getter for patient_context collection."""
    return db_manager.get_patient_context_collection()


def ping_database() -> bool:
    """Convenience getter for database health ping."""
    return db_manager.ping_database()
