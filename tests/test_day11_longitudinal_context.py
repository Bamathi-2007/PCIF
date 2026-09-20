"""
Day 11 Integration Test Suite - Database-Level Longitudinal Consolidation.

Tests:
1. Exact duplicate fast path (no LLM call, duplicate_count=1).
2. Semantic duplicate classification (DUPLICATE).
3. Value update (5h -> 7h, supersedes old, preserves history).
4. Enrichment update (attaches duration, supersedes poorer).
5. Poorer duplicate safeguard (retains richer record).
6. Distinct same category (headache vs stomach discomfort).
7. Different category (sleep vs appetite).
8. Source provenance preservation (nutrition vs mental_wellness coexist).
9. Classifier failure fallback (defaults safely to DISTINCT).
10. Update insert failure fail-safe (old record remains current).
11. Supersede update failure fail-safe (both remain current, no data loss).
12. Patient isolation (Patient A vs Patient B).
13. Current profile vs full history (5h -> 6h -> 7h chain).
14. Empty CCEE result [] handling.
15. Raw chat privacy audit (no raw conversation keys saved).
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

from ccee.schema import ClinicalContextItem
from database.mongodb import ping_database, db_manager
from database.patient_context_repository import (
    PatientContextRepository,
    FORBIDDEN_PRIVACY_KEYS,
    delete_patient_context,
    get_patient_context,
    get_current_patient_context,
)
from backend.app.services.longitudinal_context_service import (
    LongitudinalContextService,
    LongitudinalPersistenceResult,
    is_exact_normalized_duplicate,
    is_poorer_duplicate,
)
from backend.app.services.context_persistence_service import (
    ContextPersistenceService,
    ContextPersistenceResult,
)


class MockLongitudinalCollection:
    """In-memory mock MongoDB collection supporting Day 11 longitudinal context queries."""

    def __init__(self):
        self.docs: List[Dict[str, Any]] = []
        self._id_counter = 1

    def insert_many(self, documents: List[Dict[str, Any]]):
        class InsertResult:
            def __init__(self, ids):
                self.inserted_ids = ids

        inserted_ids = []
        for doc in documents:
            doc_copy = dict(doc)
            fake_id = f"mock_doc_id_{self._id_counter}"
            self._id_counter += 1
            doc_copy["_id"] = fake_id
            self.docs.append(doc_copy)
            inserted_ids.append(fake_id)
        return InsertResult(inserted_ids)

    def find(self, query: Dict[str, Any]):
        results = []
        target_pid = query.get("patient_id")
        target_source = query.get("source")
        target_category = query.get("category")
        or_conditions = query.get("$or")

        for doc in self.docs:
            if target_pid and doc.get("patient_id") != target_pid:
                continue
            if target_source and doc.get("source") != target_source:
                continue
            if target_category and doc.get("category") != target_category:
                continue

            # Evaluate $or condition for is_current
            if or_conditions:
                matches_or = False
                for cond in or_conditions:
                    if "is_current" in cond:
                        val = cond["is_current"]
                        if isinstance(val, bool) and doc.get("is_current") == val:
                            matches_or = True
                            break
                        elif isinstance(val, dict) and "$exists" in val:
                            exists_expected = val["$exists"]
                            exists_actual = "is_current" in doc
                            if exists_actual == exists_expected:
                                matches_or = True
                                break
                if not matches_or:
                    continue

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

    def update_one(self, query: Dict[str, Any], update_doc: Dict[str, Any]):
        class UpdateResult:
            def __init__(self, modified, matched):
                self.modified_count = modified
                self.matched_count = matched

        target_id = query.get("_id")
        target_pid = query.get("patient_id")

        matched = 0
        modified = 0
        set_fields = update_doc.get("$set", {})

        for doc in self.docs:
            if str(doc.get("_id")) == str(target_id):
                if target_pid and doc.get("patient_id") != target_pid:
                    continue
                matched += 1
                for k, v in set_fields.items():
                    doc[k] = v
                modified += 1
                break

        return UpdateResult(modified, matched)

    def delete_many(self, query: Dict[str, Any]):
        class DeleteResult:
            def __init__(self, count):
                self.deleted_count = count

        target_pid = query.get("patient_id")
        initial_len = len(self.docs)
        self.docs = [d for d in self.docs if d.get("patient_id") != target_pid]
        deleted = initial_len - len(self.docs)
        return DeleteResult(deleted)


class TestDay11LongitudinalContext(unittest.TestCase):
    """Test suite for Day 11 database-level longitudinal consolidation."""

    def setUp(self):
        self.mock_coll = MockLongitudinalCollection()
        self.repo = PatientContextRepository(collection=self.mock_coll)
        self.mock_llm = MagicMock()
        self.service = LongitudinalContextService(repository=self.repo, llm=self.mock_llm)

    def test_1_exact_duplicate_fast_path(self):
        """Verify that identical normalized item uses fast path without calling LLM classifier."""
        item1 = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep associated with exam stress",
            source="mental_wellness",
            value="5 hours/night",
        )
        res1 = self.service.save_longitudinal_context("patient_001", [item1])
        self.assertEqual(res1.inserted_count, 1)
        self.assertEqual(res1.duplicate_count, 0)

        # Same item again with minor spacing/case differences
        item2 = ClinicalContextItem(
            category="sleep",
            summary="  Reduced sleep associated with EXAM stress  ",
            source="mental_wellness",
            value="5 hours/night",
        )
        res2 = self.service.save_longitudinal_context("patient_001", [item2])
        self.assertEqual(res2.inserted_count, 0)
        self.assertEqual(res2.duplicate_count, 1)

        # Fast path must NOT call LLM classifier
        self.mock_llm.classify_longitudinal_relation.assert_not_called()

        records = self.repo.get_current_patient_context("patient_001")
        self.assertEqual(len(records), 1)

    def test_2_semantic_duplicate_classification(self):
        """Verify semantic duplicate classification when wording differs."""
        item1 = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep associated with exam stress",
            source="mental_wellness",
            value="5 hours/night",
        )
        self.service.save_longitudinal_context("patient_001", [item1])

        # Paraphrased item
        item2 = ClinicalContextItem(
            category="sleep",
            summary="Sleeping around five hours due to exam stress",
            source="mental_wellness",
            value="approximately 5 hours/night",
        )

        self.mock_llm.classify_longitudinal_relation.return_value = "duplicate"

        res = self.service.save_longitudinal_context("patient_001", [item2])
        self.assertEqual(res.inserted_count, 0)
        self.assertEqual(res.duplicate_count, 1)

        records = self.repo.get_current_patient_context("patient_001")
        self.assertEqual(len(records), 1)

    def test_3_value_update(self):
        """Verify value update inserts new record, supersedes old record, and preserves history."""
        item1 = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep associated with exam stress",
            source="mental_wellness",
            value="5 hours/night",
        )
        self.service.save_longitudinal_context("patient_001", [item1])
        old_record_id = self.mock_coll.docs[0]["_id"]

        # Newer item with improved sleep
        item2 = ClinicalContextItem(
            category="sleep",
            summary="Sleep duration improved following exam completion",
            source="mental_wellness",
            value="7 hours/night",
        )

        self.mock_llm.classify_longitudinal_relation.return_value = "update"

        res = self.service.save_longitudinal_context("patient_001", [item2])
        self.assertEqual(res.inserted_count, 1)
        self.assertEqual(res.superseded_count, 1)

        # Full history includes both records (oldest -> newest)
        history = self.repo.get_patient_context("patient_001")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["value"], "5 hours/night")
        self.assertEqual(history[0]["is_current"], False)
        self.assertIn("superseded_at", history[0])
        self.assertEqual(history[0]["superseded_by"], history[1]["_id"])

        self.assertEqual(history[1]["value"], "7 hours/night")
        self.assertEqual(history[1]["is_current"], True)

        # Active current profile returns ONLY the newest record
        current = self.repo.get_current_patient_context("patient_001")
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]["value"], "7 hours/night")

    def test_4_enrichment_update(self):
        """Verify that a newer item adding supported duration info supersedes poorer representation."""
        item1 = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep associated with exam stress",
            source="mental_wellness",
            value="5 hours/night",
            duration=None,
        )
        self.service.save_longitudinal_context("patient_001", [item1])

        # Newer item adds duration info
        item2 = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep associated with exam stress",
            source="mental_wellness",
            value="5 hours/night",
            duration="approximately 2 weeks",
        )

        self.mock_llm.classify_longitudinal_relation.return_value = "update"

        res = self.service.save_longitudinal_context("patient_001", [item2])
        self.assertEqual(res.inserted_count, 1)
        self.assertEqual(res.superseded_count, 1)

        current = self.repo.get_current_patient_context("patient_001")
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]["duration"], "approximately 2 weeks")

    def test_5_poorer_duplicate_safeguard(self):
        """Verify that a poorer item (lacking duration) does NOT replace a rich record."""
        item_rich = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep associated with exam stress",
            source="mental_wellness",
            value="5 hours/night",
            duration="2 weeks",
        )
        self.service.save_longitudinal_context("patient_001", [item_rich])

        # Newer poorer item missing duration
        item_poor = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep associated with exam stress",
            source="mental_wellness",
            value="5 hours/night",
            duration=None,
        )

        res = self.service.save_longitudinal_context("patient_001", [item_poor])
        self.assertEqual(res.inserted_count, 0)
        self.assertEqual(res.duplicate_count, 1)

        # Rich record remains current
        current = self.repo.get_current_patient_context("patient_001")
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]["duration"], "2 weeks")

    def test_6_distinct_same_category(self):
        """Verify distinct complaints in the same category remain distinct."""
        item1 = ClinicalContextItem(
            category="symptom",
            summary="Frequent tension headaches",
            source="mental_wellness",
        )
        self.service.save_longitudinal_context("patient_001", [item1])

        item2 = ClinicalContextItem(
            category="symptom",
            summary="Stomach discomfort after meals",
            source="mental_wellness",
        )

        self.mock_llm.classify_longitudinal_relation.return_value = "distinct"

        res = self.service.save_longitudinal_context("patient_001", [item2])
        self.assertEqual(res.inserted_count, 1)

        current = self.repo.get_current_patient_context("patient_001")
        self.assertEqual(len(current), 2)
        summaries = {r["summary"] for r in current}
        self.assertEqual(summaries, {"Frequent tension headaches", "Stomach discomfort after meals"})

    def test_7_different_category(self):
        """Verify items in different categories skip candidate matching and store as distinct."""
        item1 = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep",
            source="mental_wellness",
            value="5 hours",
        )
        self.service.save_longitudinal_context("patient_001", [item1])

        item2 = ClinicalContextItem(
            category="appetite",
            summary="Reduced appetite",
            source="mental_wellness",
        )

        res = self.service.save_longitudinal_context("patient_001", [item2])
        self.assertEqual(res.inserted_count, 1)

        # LLM not called for candidate matching because categories differ
        self.mock_llm.classify_longitudinal_relation.assert_not_called()

        current = self.repo.get_current_patient_context("patient_001")
        self.assertEqual(len(current), 2)

    def test_8_source_provenance_preservation(self):
        """Verify that items from different sources (nutrition vs mental_wellness) do NOT collapse."""
        item_nut = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep during college week",
            source="nutrition",
            value="5 hours",
        )
        item_mental = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep during college week",
            source="mental_wellness",
            value="5 hours",
        )

        self.service.save_longitudinal_context("patient_001", [item_nut])
        res = self.service.save_longitudinal_context("patient_001", [item_mental])

        self.assertEqual(res.inserted_count, 1)

        current = self.repo.get_current_patient_context("patient_001")
        self.assertEqual(len(current), 2)
        sources = {r["source"] for r in current}
        self.assertEqual(sources, {"nutrition", "mental_wellness"})

    def test_9_classifier_failure_fallback(self):
        """Verify LLM classifier error falls back safely to DISTINCT without overwriting or failing."""
        item1 = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep",
            source="mental_wellness",
            value="5 hours",
        )
        self.service.save_longitudinal_context("patient_001", [item1])

        item2 = ClinicalContextItem(
            category="sleep",
            summary="Trouble sleeping lately",
            source="mental_wellness",
            value="4-5 hours",
        )

        # Mock LLM error
        self.mock_llm.classify_longitudinal_relation.side_effect = RuntimeError("Gemini API rate limit 429")

        res = self.service.save_longitudinal_context("patient_001", [item2])
        # Service internal error handler defaults fallback to DISTINCT
        self.assertEqual(res.inserted_count, 1)

        current = self.repo.get_current_patient_context("patient_001")
        self.assertEqual(len(current), 2)

    def test_10_update_insert_failure_failsafe(self):
        """Verify fail-safe: if new update insert fails, old record remains current."""
        item1 = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep",
            source="mental_wellness",
            value="5 hours",
        )
        self.service.save_longitudinal_context("patient_001", [item1])

        item2 = ClinicalContextItem(
            category="sleep",
            summary="Improved sleep",
            source="mental_wellness",
            value="7 hours",
        )

        self.mock_llm.classify_longitudinal_relation.return_value = "update"

        # Mock repository save failure on second insert
        with patch.object(self.repo, "save_context_item", side_effect=RuntimeError("DB write failed")):
            res = self.service.save_longitudinal_context("patient_001", [item2])
            self.assertEqual(res.failed_count, 1)

        # Old record MUST remain current
        current = self.repo.get_current_patient_context("patient_001")
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]["value"], "5 hours")
        self.assertEqual(current[0]["is_current"], True)

    def test_11_supersede_failure_failsafe(self):
        """Verify fail-safe: if new insert succeeds but supersede update fails, both records remain current."""
        item1 = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep",
            source="mental_wellness",
            value="5 hours",
        )
        self.service.save_longitudinal_context("patient_001", [item1])

        item2 = ClinicalContextItem(
            category="sleep",
            summary="Improved sleep",
            source="mental_wellness",
            value="7 hours",
        )

        self.mock_llm.classify_longitudinal_relation.return_value = "update"

        with patch.object(self.repo, "mark_context_superseded", side_effect=RuntimeError("Supersede update timeout")):
            res = self.service.save_longitudinal_context("patient_001", [item2])
            self.assertEqual(res.inserted_count, 1)
            self.assertEqual(res.superseded_count, 0)

        # Both records remain current, no data lost
        current = self.repo.get_current_patient_context("patient_001")
        self.assertEqual(len(current), 2)

    def test_12_patient_isolation(self):
        """Verify candidate queries strictly isolate Patient A data from Patient B."""
        item_a = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep",
            source="mental_wellness",
            value="5 hours",
        )
        item_b = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep",
            source="mental_wellness",
            value="5 hours",
        )

        self.service.save_longitudinal_context("patient_A", [item_a])
        self.service.save_longitudinal_context("patient_B", [item_b])

        curr_a = self.repo.get_current_patient_context("patient_A")
        curr_b = self.repo.get_current_patient_context("patient_B")

        self.assertEqual(len(curr_a), 1)
        self.assertEqual(curr_a[0]["patient_id"], "patient_A")
        self.assertEqual(len(curr_b), 1)
        self.assertEqual(curr_b[0]["patient_id"], "patient_B")

    def test_13_current_vs_history_chain(self):
        """Verify chain of updates (5h -> 6h -> 7h) returns full 3-item history but 1 current profile item."""
        item1 = ClinicalContextItem(category="sleep", summary="Sleep", source="mental_wellness", value="5 hours")
        item2 = ClinicalContextItem(category="sleep", summary="Sleep", source="mental_wellness", value="6 hours")
        item3 = ClinicalContextItem(category="sleep", summary="Sleep", source="mental_wellness", value="7 hours")

        self.mock_llm.classify_longitudinal_relation.return_value = "update"

        self.service.save_longitudinal_context("patient_001", [item1])
        self.service.save_longitudinal_context("patient_001", [item2])
        self.service.save_longitudinal_context("patient_001", [item3])

        # History view
        history = self.repo.get_patient_context("patient_001")
        self.assertEqual(len(history), 3)
        values = [r["value"] for r in history]
        self.assertEqual(values, ["5 hours", "6 hours", "7 hours"])
        self.assertEqual([r["is_current"] for r in history], [False, False, True])

        # Active current profile view
        current = self.repo.get_current_patient_context("patient_001")
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]["value"], "7 hours")

    def test_14_empty_ccee_result_handling(self):
        """Verify ContextPersistenceService with [] does zero DB operations and leaves old records intact."""
        item1 = ClinicalContextItem(category="sleep", summary="Sleep", source="mental_wellness", value="5 hours")
        self.service.save_longitudinal_context("patient_001", [item1])

        mock_ccee = MagicMock()
        mock_ccee.extract_context.return_value = []  # Empty CCEE extraction

        cps = ContextPersistenceService(
            ccee=mock_ccee,
            repository=self.repo,
            longitudinal_service=self.service,
        )

        res = cps.extract_and_persist_context(
            patient_id="patient_001",
            conversation="I'm not having appetite problems anymore.",
            source="mental_wellness",
        )

        self.assertEqual(res.status, "no_relevant_context")
        self.assertEqual(res.saved_count, 0)

        # Existing sleep context MUST remain untouched and current
        current = self.repo.get_current_patient_context("patient_001")
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]["value"], "5 hours")

    def test_15_raw_chat_privacy_audit(self):
        """Verify stored documents with is_current metadata NEVER contain forbidden raw chat keys."""
        item = ClinicalContextItem(
            category="nutrition",
            summary="Low water intake",
            source="nutrition",
            value="1 glass",
        )
        self.service.save_longitudinal_context("patient_privacy", [item])

        docs = self.repo.get_patient_context("patient_privacy")
        self.assertEqual(len(docs), 1)
        doc = docs[0]

        for forbidden_key in FORBIDDEN_PRIVACY_KEYS:
            self.assertNotIn(
                forbidden_key,
                doc,
                f"Privacy Violation: Found forbidden raw conversation key '{forbidden_key}' in document!"
            )


class TestDay11LiveIntegrationTests(unittest.TestCase):
    """Live MongoDB integration tests for Day 11 (runs if MONGODB_URI is available)."""

    @classmethod
    def setUpClass(cls):
        if os.getenv("MONGODB_URI"):
            db_manager._uri = os.getenv("MONGODB_URI")
        cls.db_available = ping_database()
        if not cls.db_available:
            print("\n[INFO] Live MongoDB not reachable or URI missing. Skipping live integration tests.")

    def setUp(self):
        if not self.db_available:
            self.skipTest("MongoDB instance not reachable.")
        delete_patient_context("day11_live_patient")

    def tearDown(self):
        if self.db_available:
            delete_patient_context("day11_live_patient")

    def test_live_longitudinal_exact_and_current_queries(self):
        """Verify live MongoDB storage of is_current and get_current_patient_context queries."""
        item1 = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep associated with exam stress",
            source="mental_wellness",
            value="5 hours/night",
        )
        item2 = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep associated with exam stress",
            source="mental_wellness",
            value="5 hours/night",
        )

        service = LongitudinalContextService()
        res1 = service.save_longitudinal_context("day11_live_patient", [item1])
        res2 = service.save_longitudinal_context("day11_live_patient", [item2])

        self.assertEqual(res1.inserted_count, 1)
        self.assertEqual(res2.duplicate_count, 1)

        history = get_patient_context("day11_live_patient")
        current = get_current_patient_context("day11_live_patient")

        self.assertEqual(len(history), 1)
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]["is_current"], True)


def run_day11_tests():
    print("======================================================================")
    print("       PCIF DAY 11 LONGITUDINAL CONSOLIDATION TEST SUITE             ")
    print("======================================================================")
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDay11LongitudinalContext))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDay11LiveIntegrationTests))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_day11_tests()
    sys.exit(0 if success else 1)
