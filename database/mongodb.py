"""
MongoDB Database Connection & Schema Stub.

Logical Collections:
1. `users` - Patient and Doctor account profiles.
2. `patient_context` - Longitudinal context items extracted by CCEE or entered by doctor.
3. `doctor_notes` - Consultation records and confirmed clinical findings.
"""

from typing import Dict, Any, List


class MongoDBManager:
    """
    Placeholder manager for future MongoDB integration (Days 9-11).
    """

    def __init__(self, uri: str = "mongodb://localhost:27017", db_name: str = "pcif_database"):
        self.uri = uri
        self.db_name = db_name
        self.connected = False
        print(f"[Database Placeholder] Configured for URI '{self.uri}', DB '{self.db_name}'. Connection inactive.")

    def get_status(self) -> Dict[str, Any]:
        """Returns database connection status placeholder."""
        return {
            "connected": self.connected,
            "uri": self.uri,
            "db_name": self.db_name,
            "collections": ["users", "patient_context", "doctor_notes"],
            "status": "Placeholder mode (Days 9-11 scheduled integration)"
        }

    def store_context_item(self, context_item: Dict[str, Any]) -> bool:
        """Placeholder method for inserting extracted context."""
        print(f"[Database Placeholder] Received record from source '{context_item.get('source')}'. Storage skipped for Day 1.")
        return True

    def get_patient_longitudinal_context(self, patient_id: str) -> List[Dict[str, Any]]:
        """Placeholder method for retrieving patient context history."""
        print(f"[Database Placeholder] Context query for patient '{patient_id}'. Returning mock empty timeline.")
        return []
