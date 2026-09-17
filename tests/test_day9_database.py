"""
Day 9 Database Test Suite - Shared Database Foundation & Patient Context Persistence.

Runs:
1. Local Unit Tests (Validation, Explicit URI requirement, Privacy, Dict conversion, Boundary conditions)
2. Live MongoDB Integration Tests (Ping, Shared Patient Context, Isolation, Ordering, Clean ObjectId conversion, Cleanup)
"""

import os
import sys
import unittest
from datetime import datetime, timezone
from typing import List, Dict, Any
from dotenv import load_dotenv

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables (.env) before database module import
load_dotenv()

# Force UTF-8 output encoding for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from ccee.schema import ClinicalContextItem
from database.mongodb import MongoDBManager, db_manager, ping_database
from database.patient_context_repository import (
    PatientContextRepository,
    FORBIDDEN_PRIVACY_KEYS,
    save_context_item,
    save_context_items,
    get_patient_context,
    delete_patient_context,
)


class MockCollection:
    """In-memory mock MongoDB collection for offline unit testing."""

    def __init__(self):
        self.docs: List[Dict[str, Any]] = []
        self.inserted_count = 0
        self.deleted_count = 0

    def insert_many(self, documents: List[Dict[str, Any]]):
        class InsertResult:
            def __init__(self, ids):
                self.inserted_ids = ids

        inserted_ids = []
        for i, doc in enumerate(documents):
            doc_copy = dict(doc)
            fake_id = f"mock_id_{len(self.docs) + 1}"
            doc_copy["_id"] = fake_id
            self.docs.append(doc_copy)
            inserted_ids.append(fake_id)
        return InsertResult(inserted_ids)

    def find(self, query: Dict[str, Any]):
        results = []
        target_pid = query.get("patient_id")
        for doc in self.docs:
            if doc.get("patient_id") == target_pid:
                results.append(dict(doc))

        class MockCursor:
            def __init__(self, items):
                self._items = items

            def sort(self, key, direction):
                if key == "captured_at":
                    reverse = direction < 0
                    self._items.sort(key=lambda x: x.get("captured_at"), reverse=reverse)
                return self

            def __iter__(self):
                return iter(self._items)

        return MockCursor(results)

    def delete_many(self, query: Dict[str, Any]):
        class DeleteResult:
            def __init__(self, count):
                self.deleted_count = count

        target_pid = query.get("patient_id")
        initial_len = len(self.docs)
        self.docs = [d for d in self.docs if d.get("patient_id") != target_pid]
        deleted = initial_len - len(self.docs)
        return DeleteResult(deleted)


class TestDay9LocalUnitTests(unittest.TestCase):
    """Local unit tests for persistence logic and privacy validation."""

    def setUp(self):
        self.mock_coll = MockCollection()
        self.repo = PatientContextRepository(collection=self.mock_coll)

    def test_missing_mongodb_uri_raises_controlled_error(self):
        """Missing MONGODB_URI (None) must raise controlled ConnectionError."""
        mgr = MongoDBManager(uri=None)
        mgr._uri = None
        with self.assertRaises(ConnectionError) as ctx:
            mgr.get_client()
        self.assertIn("Configuration Error", str(ctx.exception))
        self.assertNotIn("mongodb://", str(ctx.exception))

    def test_blank_mongodb_uri_raises_controlled_error(self):
        """Blank MONGODB_URI ("  ") must raise controlled ConnectionError."""
        mgr = MongoDBManager(uri="   ")
        with self.assertRaises(ConnectionError) as ctx:
            mgr.get_client()
        self.assertIn("Configuration Error", str(ctx.exception))

    def test_blank_patient_id_rejected(self):
        """Blank or empty patient_id must raise ValueError."""
        item = ClinicalContextItem(
            category="hydration",
            summary="Low water intake",
            source="nutrition",
        )
        with self.assertRaises(ValueError):
            self.repo.save_context_items("", [item])
        with self.assertRaises(ValueError):
            self.repo.save_context_items("   ", [item])
        with self.assertRaises(ValueError):
            self.repo.get_patient_context("")

    def test_empty_items_list_inserts_nothing(self):
        """Empty items list [] must insert nothing and return []."""
        result = self.repo.save_context_items("patient_demo_001", [])
        self.assertEqual(result, [])
        self.assertEqual(len(self.mock_coll.docs), 0)

    def test_prepare_document_attaches_utc_captured_at_and_omits_nones(self):
        """Verify patient_id, captured_at UTC are attached and None fields omitted."""
        item = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep associated with exam stress",
            source="mental_wellness",
            record_type="patient_reported",
            value="5 hours/night",
            duration=None,  # Optional None field
        )
        doc = PatientContextRepository.prepare_document("patient_demo_001", item)

        self.assertEqual(doc["patient_id"], "patient_demo_001")
        self.assertEqual(doc["category"], "sleep")
        self.assertEqual(doc["summary"], "Reduced sleep associated with exam stress")
        self.assertEqual(doc["source"], "mental_wellness")
        self.assertEqual(doc["record_type"], "patient_reported")
        self.assertEqual(doc["value"], "5 hours/night")
        self.assertNotIn("duration", doc)  # Must be omitted
        self.assertIn("captured_at", doc)
        self.assertIsInstance(doc["captured_at"], datetime)
        self.assertIsNotNone(doc["captured_at"].tzinfo)
        self.assertEqual(doc["captured_at"].tzinfo, timezone.utc)

    def test_privacy_check_forbidden_keys(self):
        """Verify forbidden raw conversation keys trigger error or are absent."""
        item = ClinicalContextItem(
            category="nutrition",
            summary="Skipped lunch due to meetings",
            source="nutrition",
        )
        doc = PatientContextRepository.prepare_document("patient_demo_001", item)

        for key in FORBIDDEN_PRIVACY_KEYS:
            self.assertNotIn(key, doc, f"Forbidden privacy key '{key}' found in prepared document!")

    def test_item_immutability(self):
        """Saving context items must not mutate the original ClinicalContextItem object."""
        item = ClinicalContextItem(
            category="hydration",
            summary="Low water intake",
            source="nutrition",
            value="1 glass",
        )
        original_dict = dict(item.to_dict())

        self.repo.save_context_items("patient_demo_001", [item])

        self.assertEqual(item.to_dict(), original_dict)
        self.assertFalse(hasattr(item, "patient_id"))
        self.assertFalse(hasattr(item, "captured_at"))

    def test_mock_repository_save_and_retrieve(self):
        """Verify save and retrieve flow on mock collection without raw Mongo types."""
        nut_item = ClinicalContextItem(
            category="hydration",
            summary="Low water intake during college hours",
            source="nutrition",
            value="1 glass/day",
        )
        men_item = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep associated with exam stress",
            source="mental_wellness",
            value="5 hours/night",
            duration="this week",
        )

        inserted_ids = self.repo.save_context_items("patient_demo_001", [nut_item, men_item])
        self.assertEqual(len(inserted_ids), 2)

        records = self.repo.get_patient_context("patient_demo_001")
        self.assertEqual(len(records), 2)

        for rec in records:
            self.assertIsInstance(rec["_id"], str)
            self.assertNotEqual(type(rec["_id"]).__name__, "ObjectId")

        sources = {r["source"] for r in records}
        self.assertEqual(sources, {"nutrition", "mental_wellness"})


class TestDay9LiveIntegrationTests(unittest.TestCase):
    """Live MongoDB integration tests (Runs if explicit MONGODB_URI is available)."""

    @classmethod
    def setUpClass(cls):
        # Refresh URI from env if set
        if os.getenv("MONGODB_URI"):
            db_manager._uri = os.getenv("MONGODB_URI")
        cls.db_available = ping_database()
        if not cls.db_available:
            print("\n[INFO] Live MongoDB not reachable or URI missing. Skipping live integration tests.")

    def setUp(self):
        if not self.db_available:
            self.skipTest("MongoDB instance not reachable.")
        delete_patient_context("patient_demo_001")
        delete_patient_context("patient_demo_002")

    def tearDown(self):
        if self.db_available:
            delete_patient_context("patient_demo_001")
            delete_patient_context("patient_demo_002")

    def test_live_ping(self):
        """Verify live database connection ping."""
        self.assertTrue(ping_database())

    def test_shared_patient_context_persistence(self):
        """Verify Nutrition AI and Mental Wellness AI records coexist under same patient_id."""
        nut_item = ClinicalContextItem(
            category="hydration",
            summary="Low water intake during college hours",
            source="nutrition",
            record_type="patient_reported",
            value="1 glass on some days",
        )
        men_item = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep associated with exam stress",
            source="mental_wellness",
            record_type="patient_reported",
            value="5 hours/night",
            duration="this week",
        )

        ids = save_context_items("patient_demo_001", [nut_item, men_item])
        self.assertEqual(len(ids), 2)

        records = get_patient_context("patient_demo_001")
        self.assertEqual(len(records), 2)

        categories = {r["category"] for r in records}
        sources = {r["source"] for r in records}

        self.assertEqual(categories, {"hydration", "sleep"})
        self.assertEqual(sources, {"nutrition", "mental_wellness"})

    def test_retrieval_does_not_leak_raw_object_id(self):
        """Verify get_patient_context converts _id to str and does not return bson.ObjectId."""
        item = ClinicalContextItem(
            category="mood",
            summary="Mild exam anxiety",
            source="mental_wellness",
        )
        save_context_item("patient_demo_001", item)

        records = get_patient_context("patient_demo_001")
        self.assertEqual(len(records), 1)
        rec = records[0]

        self.assertIsInstance(rec["_id"], str)
        self.assertNotEqual(type(rec["_id"]).__name__, "ObjectId")

    def test_patient_isolation(self):
        """Verify get_patient_context for patient 1 NEVER returns records for patient 2."""
        item1 = ClinicalContextItem(
            category="nutrition",
            summary="High sugar intake",
            source="nutrition",
        )
        item2 = ClinicalContextItem(
            category="stress",
            summary="High exam anxiety",
            source="mental_wellness",
        )

        save_context_item("patient_demo_001", item1)
        save_context_item("patient_demo_002", item2)

        records_p1 = get_patient_context("patient_demo_001")
        records_p2 = get_patient_context("patient_demo_002")

        self.assertEqual(len(records_p1), 1)
        self.assertEqual(records_p1[0]["category"], "nutrition")
        self.assertEqual(records_p1[0]["patient_id"], "patient_demo_001")

        self.assertEqual(len(records_p2), 1)
        self.assertEqual(records_p2[0]["category"], "stress")
        self.assertEqual(records_p2[0]["patient_id"], "patient_demo_002")

    def test_temporal_ordering(self):
        """Verify retrieved records are sorted from oldest to newest by captured_at."""
        item1 = ClinicalContextItem(category="mood", summary="Anxious", source="mental_wellness")
        item2 = ClinicalContextItem(category="sleep", summary="Poor sleep", source="mental_wellness")

        save_context_item("patient_demo_001", item1)
        save_context_item("patient_demo_001", item2)

        records = get_patient_context("patient_demo_001")
        self.assertEqual(len(records), 2)

        t1 = records[0]["captured_at"]
        t2 = records[1]["captured_at"]
        self.assertLessEqual(t1, t2)

    def test_raw_conversation_safety_assertion(self):
        """Directly inspect stored MongoDB documents to ensure zero raw chat keys exist."""
        item = ClinicalContextItem(
            category="activity",
            summary="Reduced physical exercise",
            source="nutrition",
        )
        save_context_item("patient_demo_001", item)

        records = get_patient_context("patient_demo_001")
        self.assertEqual(len(records), 1)
        doc = records[0]

        for forbidden_key in FORBIDDEN_PRIVACY_KEYS:
            self.assertNotIn(
                forbidden_key,
                doc,
                f"PRIVACY VIOLATION: Found raw conversation key '{forbidden_key}' in MongoDB document!"
            )


def run_day9_tests():
    print("======================================================================")
    print("         PCIF DAY 9 DATABASE & PERSISTENCE TEST SUITE                 ")
    print("======================================================================")
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDay9LocalUnitTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDay9LiveIntegrationTests))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_day9_tests()
    sys.exit(0 if success else 1)
