"""
Day 14 Integration Test Suite - Clinician-Authored Note Persistence.

Tests:
1. Save Note: Verify patient_id, note, doctor_confirmed record_type, and created_at.
2. Server-Controlled Provenance: Caller cannot force patient_reported; stored record is always doctor_confirmed.
3. Patient Isolation: Patient A notes never appear for Patient B.
4. Empty Retrieval: Unknown synthetic ID returns empty list notes = [].
5. Invalid Input: Blank or whitespace-only patient_id / note raises ValueError and results in no DB write.
6. patient_context Separation: patient_context count remains completely unchanged before and after doctor note save.
7. No CCEE: Saving a doctor note never invokes CCEE extraction or modifies CCEE schemas.
8. No Longitudinal Consolidation: Multiple notes for the same patient are preserved as independent append-only records without superseding.
9. DB Failure: Repository and API return controlled failures on database error; never fake empty success.
10. Privacy & Storage Shape: doctor_notes records never contain raw conversation, chat history, or assistant responses.
11. API End-to-End: POST /api/doctor/notes and GET /api/doctor/notes/{patient_id} endpoints validate contracts and avoid raw ObjectIds.
"""

import os
import sys
import unittest
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables before imports
load_dotenv()

# Force UTF-8 output encoding for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from backend.main import app
from ccee.schema import ClinicalContextItem
from database.mongodb import get_patient_context_collection, get_doctor_notes_collection
from database.patient_context_repository import (
    PatientContextRepository,
    save_context_item,
    get_patient_context,
    delete_patient_context,
)
from database.doctor_notes_repository import (
    DoctorNotesRepository,
    save_doctor_note,
    get_doctor_notes,
    delete_doctor_notes,
    FORBIDDEN_PRIVACY_KEYS,
)

client = TestClient(app)


class MockDoctorNotesCollection:
    """In-memory mock MongoDB collection for doctor_notes."""

    def __init__(self):
        self.docs: List[Dict[str, Any]] = []
        self._id_counter = 1

    def insert_one(self, doc: Dict[str, Any]):
        new_doc = dict(doc)
        new_id = f"mock_note_id_{self._id_counter}"
        self._id_counter += 1
        new_doc["_id"] = new_id
        self.docs.append(new_doc)
        mock_result = MagicMock()
        mock_result.inserted_id = new_id
        return mock_result

    def find(self, query: Dict[str, Any]):
        patient_id = query.get("patient_id")
        matches = [d for d in self.docs if d.get("patient_id") == patient_id]

        class MockCursor:
            def __init__(self, data):
                self._data = list(data)

            def sort(self, key, direction):
                if direction == -1 or direction == "desc" or direction == 2:
                    self._data.sort(key=lambda x: x.get(key, datetime.min), reverse=True)
                else:
                    self._data.sort(key=lambda x: x.get(key, datetime.min))
                return self

            def __iter__(self):
                return iter(self._data)

        return MockCursor(matches)

    def delete_many(self, query: Dict[str, Any]):
        patient_id = query.get("patient_id")
        initial_len = len(self.docs)
        self.docs = [d for d in self.docs if d.get("patient_id") != patient_id]
        deleted_count = initial_len - len(self.docs)
        mock_res = MagicMock()
        mock_res.deleted_count = deleted_count
        return mock_res


class TestDay14DoctorNotes(unittest.TestCase):
    """Unit and integration test cases for Day 14 Doctor Notes persistence."""

    def setUp(self):
        self.mock_coll = MockDoctorNotesCollection()
        self.repo = DoctorNotesRepository(collection=self.mock_coll)

    def test_1_save_note(self):
        """1. Save note: Verify patient_id, note, doctor_confirmed record_type, and created_at."""
        saved = self.repo.save_doctor_note(
            patient_id="PAT_001",
            note="Reviewed fatigue symptoms. Recommended thyroid panel and routine blood work."
        )

        self.assertIn("id", saved)
        self.assertEqual(saved["patient_id"], "PAT_001")
        self.assertEqual(saved["note"], "Reviewed fatigue symptoms. Recommended thyroid panel and routine blood work.")
        self.assertEqual(saved["record_type"], "doctor_confirmed")
        self.assertIsInstance(saved["created_at"], datetime)

        # Verify underlying stored document
        self.assertEqual(len(self.mock_coll.docs), 1)
        stored = self.mock_coll.docs[0]
        self.assertEqual(stored["patient_id"], "PAT_001")
        self.assertEqual(stored["note"], "Reviewed fatigue symptoms. Recommended thyroid panel and routine blood work.")
        self.assertEqual(stored["record_type"], "doctor_confirmed")
        self.assertIsInstance(stored["created_at"], datetime)

    def test_2_server_controlled_provenance(self):
        """2. Server-controlled provenance: Stored record is ALWAYS doctor_confirmed."""
        saved = self.repo.save_doctor_note(
            patient_id="PAT_PROV",
            note="Confirmed normal neurological exam."
        )
        self.assertEqual(saved["record_type"], "doctor_confirmed")

        stored = self.mock_coll.docs[0]
        self.assertEqual(stored["record_type"], "doctor_confirmed")
        self.assertNotEqual(stored["record_type"], "patient_reported")

    def test_3_patient_isolation(self):
        """3. Patient isolation: Patient A notes never appear for Patient B."""
        self.repo.save_doctor_note("PAT_A", "Clinician note for Patient A")
        self.repo.save_doctor_note("PAT_B", "Clinician note for Patient B")

        notes_a = self.repo.get_doctor_notes("PAT_A")
        notes_b = self.repo.get_doctor_notes("PAT_B")

        self.assertEqual(len(notes_a), 1)
        self.assertEqual(notes_a[0]["note"], "Clinician note for Patient A")
        self.assertEqual(notes_a[0]["patient_id"], "PAT_A")

        self.assertEqual(len(notes_b), 1)
        self.assertEqual(notes_b[0]["note"], "Clinician note for Patient B")
        self.assertEqual(notes_b[0]["patient_id"], "PAT_B")

    def test_4_empty_retrieval(self):
        """4. Empty retrieval: Unknown synthetic ID returns empty list notes = []."""
        notes = self.repo.get_doctor_notes("SYNTHETIC_UNKNOWN_PATIENT_999")
        self.assertIsInstance(notes, list)
        self.assertEqual(len(notes), 0)

    def test_5_invalid_input_validation(self):
        """5. Invalid input: Blank or whitespace-only patient_id / note -> no DB write."""
        initial_count = len(self.mock_coll.docs)

        # Blank patient_id
        with self.assertRaises(ValueError):
            self.repo.save_doctor_note("", "Valid note")
        self.assertEqual(len(self.mock_coll.docs), initial_count)

        # Whitespace patient_id
        with self.assertRaises(ValueError):
            self.repo.save_doctor_note("   ", "Valid note")
        self.assertEqual(len(self.mock_coll.docs), initial_count)

        # Blank note
        with self.assertRaises(ValueError):
            self.repo.save_doctor_note("PAT_001", "")
        self.assertEqual(len(self.mock_coll.docs), initial_count)

        # Whitespace note
        with self.assertRaises(ValueError):
            self.repo.save_doctor_note("PAT_001", "   \t\n  ")
        self.assertEqual(len(self.mock_coll.docs), initial_count)

    def test_6_patient_context_separation(self):
        """6. patient_context separation: Saving doctor note does NOT alter patient_context."""
        # Use real database / mock repository to count patient_context before and after
        test_patient_id = "test_day14_separation_patient"
        delete_patient_context(test_patient_id)
        delete_doctor_notes(test_patient_id)

        try:
            # Seed 1 patient_context record
            item = ClinicalContextItem(
                category="nutrition",
                summary="Reduced appetite reported by patient",
                source="nutrition",
            )
            save_context_item(test_patient_id, item)

            context_before = get_patient_context(test_patient_id)
            count_before = len(context_before)
            self.assertEqual(count_before, 1)

            # Save doctor note into doctor_notes
            save_doctor_note(test_patient_id, "Doctor confirmed normal abdominal examination.")

            # Verify patient_context count and records remain strictly unchanged
            context_after = get_patient_context(test_patient_id)
            self.assertEqual(len(context_after), count_before)
            self.assertEqual(context_after[0]["summary"], "Reduced appetite reported by patient")
            self.assertEqual(context_after[0]["record_type"], "patient_reported")

            # Verify doctor note exists in doctor_notes
            doctor_notes = get_doctor_notes(test_patient_id)
            self.assertEqual(len(doctor_notes), 1)
            self.assertEqual(doctor_notes[0]["record_type"], "doctor_confirmed")
        finally:
            delete_patient_context(test_patient_id)
            delete_doctor_notes(test_patient_id)

    def test_7_no_ccee_invocation(self):
        """7. No CCEE: Saving doctor note must NOT invoke CCEE extraction engine."""
        with patch("ccee.engine.ClinicalContextExtractionEngine.extract_context") as mock_ccee:
            self.repo.save_doctor_note("PAT_NO_CCEE", "Doctor evaluated cardiology status.")
            mock_ccee.assert_not_called()

    def test_8_no_longitudinal_consolidation_append_only(self):
        """8. No longitudinal consolidation: Multiple notes remain independent, append-only records."""
        t1 = datetime(2026, 9, 20, 10, 0, 0, tzinfo=timezone.utc)
        t2 = datetime(2026, 9, 21, 14, 0, 0, tzinfo=timezone.utc)

        with patch("database.doctor_notes_repository.datetime") as mock_dt:
            mock_dt.now.return_value = t1
            self.repo.save_doctor_note("PAT_APPEND", "First note: ordered lab tests.")

            mock_dt.now.return_value = t2
            self.repo.save_doctor_note("PAT_APPEND", "Second note: lab results reviewed normal.")

        notes = self.repo.get_doctor_notes("PAT_APPEND")
        self.assertEqual(len(notes), 2)

        # Newest-first ordering
        self.assertEqual(notes[0]["note"], "Second note: lab results reviewed normal.")
        self.assertEqual(notes[1]["note"], "First note: ordered lab tests.")

        # Verify no superseding metadata present
        for n in notes:
            self.assertNotIn("is_current", n)
            self.assertNotIn("superseded_by", n)
            self.assertNotIn("superseded_at", n)

    def test_9_database_failure_resilience(self):
        """9. DB failure: Controlled server failure; never return fake empty success."""
        mock_failing_coll = MagicMock()
        mock_failing_coll.insert_one.side_effect = Exception("MongoDB connection lost")
        mock_failing_coll.find.side_effect = Exception("MongoDB query timeout")

        failing_repo = DoctorNotesRepository(collection=mock_failing_coll)

        # Save failure must raise RuntimeError
        with self.assertRaises(RuntimeError) as ctx_save:
            failing_repo.save_doctor_note("PAT_FAIL", "Test note")
        self.assertIn("Database operation failed", str(ctx_save.exception))

        # Get failure must raise RuntimeError (NOT return [])
        with self.assertRaises(RuntimeError) as ctx_get:
            failing_repo.get_doctor_notes("PAT_FAIL")
        self.assertIn("Database operation failed", str(ctx_get.exception))

    def test_10_privacy_and_storage_shape(self):
        """10. Privacy/storage shape: doctor_notes must not contain raw chat keys."""
        saved = self.repo.save_doctor_note("PAT_PRIVACY", "Attending review note.")

        stored_doc = self.mock_coll.docs[0]
        for forbidden in FORBIDDEN_PRIVACY_KEYS:
            self.assertNotIn(forbidden, stored_doc)
            self.assertNotIn(forbidden, saved)


class TestDay14DoctorNotesAPI(unittest.TestCase):
    """API endpoint integration tests for POST and GET /api/doctor/notes."""

    def setUp(self):
        delete_doctor_notes("day14_test_api_patient")

    def tearDown(self):
        delete_doctor_notes("day14_test_api_patient")

    def test_post_and_get_doctor_notes_api_end_to_end(self):
        """Test full save and retrieval flow via HTTP endpoints."""
        patient_id = "day14_test_api_patient"

        # 1. Initially empty retrieval
        get_res_empty = client.get(f"/api/doctor/notes/{patient_id}")
        self.assertEqual(get_res_empty.status_code, 200)
        data_empty = get_res_empty.json()
        self.assertEqual(data_empty["patient_id"], patient_id)
        self.assertEqual(data_empty["notes"], [])

        # 2. Save clinician note
        post_res = client.post(
            "/api/doctor/notes",
            json={
                "patient_id": patient_id,
                "note": "Clinician personally reviewed patient fatigue and verified no red flag symptoms."
            }
        )
        self.assertEqual(post_res.status_code, 200)
        post_data = post_res.json()
        self.assertEqual(post_data["status"], "saved")
        self.assertIn("note", post_data)
        saved_note = post_data["note"]
        self.assertEqual(saved_note["patient_id"], patient_id)
        self.assertEqual(saved_note["record_type"], "doctor_confirmed")
        self.assertIn("id", saved_note)
        self.assertIsInstance(saved_note["id"], str)
        self.assertIn("created_at", saved_note)

        # 3. Retrieve notes
        get_res = client.get(f"/api/doctor/notes/{patient_id}")
        self.assertEqual(get_res.status_code, 200)
        get_data = get_res.json()
        self.assertEqual(get_data["patient_id"], patient_id)
        self.assertEqual(len(get_data["notes"]), 1)
        retrieved_note = get_data["notes"][0]
        self.assertEqual(retrieved_note["note"], "Clinician personally reviewed patient fatigue and verified no red flag symptoms.")
        self.assertEqual(retrieved_note["record_type"], "doctor_confirmed")
        self.assertIsInstance(retrieved_note["id"], str)

    def test_post_doctor_notes_validation(self):
        """Test API validation for blank or whitespace inputs."""
        # Blank patient_id
        res1 = client.post("/api/doctor/notes", json={"patient_id": "", "note": "Some note"})
        self.assertEqual(res1.status_code, 422)

        # Whitespace patient_id
        res2 = client.post("/api/doctor/notes", json={"patient_id": "   ", "note": "Some note"})
        self.assertEqual(res2.status_code, 422)

        # Blank note
        res3 = client.post("/api/doctor/notes", json={"patient_id": "PAT_001", "note": ""})
        self.assertEqual(res3.status_code, 422)

        # Whitespace note
        res4 = client.post("/api/doctor/notes", json={"patient_id": "PAT_001", "note": "   "})
        self.assertEqual(res4.status_code, 422)


def run_day14_tests():
    print("======================================================================")
    print("          PCIF DAY 14 CLINICIAN NOTES PERSISTENCE TEST SUITE          ")
    print("======================================================================")
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDay14DoctorNotes))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDay14DoctorNotesAPI))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_day14_tests()
    sys.exit(0 if success else 1)
