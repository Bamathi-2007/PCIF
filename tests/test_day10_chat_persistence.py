"""
Day 10 Integration Test Suite - Connecting Patient Chat, CCEE, and MongoDB patient_context.

Verifies:
1. Shared Patient Context (Nutrition + Mental Wellness coexistence under same patient_id).
2. Patient Isolation (Patient A context never leaks to Patient B).
3. Irrelevant Conversation Handling (no_relevant_context status, 0 DB inserts).
4. Storage Failure Resilience (chat response survives DB failure, status='failed', no secret leakage).
5. CCEE Extraction Failure Resilience (chat response survives LLM error, status='failed', no DB call).
6. Raw Conversation Privacy Safeguard (zero raw chat keys saved in MongoDB).
7. Request Input Validation (reject missing/empty/whitespace patient_id).
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables before app imports
load_dotenv()

# Force UTF-8 output encoding for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from backend.main import app
from ccee.schema import ClinicalContextItem
from database.mongodb import ping_database
from database.patient_context_repository import (
    get_patient_context,
    delete_patient_context,
    FORBIDDEN_PRIVACY_KEYS,
)
from backend.app.services.context_persistence_service import context_persistence_service

client = TestClient(app)


class TestDay10ChatPersistence(unittest.TestCase):
    """Integration test suite for Day 10 PCIF chat persistence flow."""

    def setUp(self):
        """Clean up synthetic test patient records before each test."""
        self.shared_patient_id = "day10_shared_patient_test"
        self.patient_a = "day10_patient_a_test"
        self.patient_b = "day10_patient_b_test"
        self.irrelevant_patient = "day10_irrelevant_patient_test"
        self.storage_fail_patient = "day10_storage_fail_patient_test"
        self.ccee_fail_patient = "day10_ccee_fail_patient_test"
        self.privacy_patient = "day10_privacy_patient_test"

        for pid in [
            self.shared_patient_id,
            self.patient_a,
            self.patient_b,
            self.irrelevant_patient,
            self.storage_fail_patient,
            self.ccee_fail_patient,
            self.privacy_patient,
        ]:
            delete_patient_context(pid)

    def tearDown(self):
        """Clean up synthetic test patient records after each test."""
        for pid in [
            self.shared_patient_id,
            self.patient_a,
            self.patient_b,
            self.irrelevant_patient,
            self.storage_fail_patient,
            self.ccee_fail_patient,
            self.privacy_patient,
        ]:
            delete_patient_context(pid)

    def test_request_validation_missing_patient_id(self):
        """Verify that requests missing patient_id, or with empty/whitespace patient_id, are rejected."""
        # 1. Missing patient_id
        res = client.post("/api/nutrition/chat", json={"message": "I eat vegetables."})
        self.assertEqual(res.status_code, 422)

        # 2. Empty patient_id
        res = client.post("/api/nutrition/chat", json={"patient_id": "", "message": "I eat vegetables."})
        self.assertEqual(res.status_code, 422)

        # 3. Whitespace-only patient_id
        res = client.post("/api/mental-wellness/chat", json={"patient_id": "   ", "message": "I feel stressed."})
        self.assertEqual(res.status_code, 422)

    def test_irrelevant_conversation(self):
        """Verify that irrelevant conversation extracts [] and returns status 'no_relevant_context' with 0 DB inserts."""
        response = client.post(
            "/api/nutrition/chat",
            json={
                "patient_id": self.irrelevant_patient,
                "message": "My favourite colour is yellow.",
                "history": []
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("context_persistence", data)
        self.assertEqual(data["context_persistence"]["status"], "no_relevant_context")
        self.assertEqual(data["context_persistence"]["saved_count"], 0)

        # Confirm zero MongoDB documents persisted
        stored_items = get_patient_context(self.irrelevant_patient)
        self.assertEqual(len(stored_items), 0)

    def test_end_to_end_shared_patient_context(self):
        """
        Verify primary Day 10 primary flow:
        Nutrition AI conversation + Mental Wellness AI conversation coexist under SAME patient_id.
        """
        # Step 1: Nutrition AI interaction
        nut_res = client.post(
            "/api/nutrition/chat",
            json={
                "patient_id": self.shared_patient_id,
                "message": "I barely drink water during college and some days only have one glass.",
                "history": []
            }
        )
        self.assertEqual(nut_res.status_code, 200)
        nut_data = nut_res.json()
        self.assertIn("reply", nut_data)
        self.assertEqual(nut_data["source"], "nutrition")
        self.assertEqual(nut_data["context_persistence"]["status"], "saved")
        self.assertGreaterEqual(nut_data["context_persistence"]["saved_count"], 1)

        # Step 2: Mental Wellness AI interaction under SAME patient_id
        mental_res = client.post(
            "/api/mental-wellness/chat",
            json={
                "patient_id": self.shared_patient_id,
                "message": "I've been sleeping around five hours because I'm stressed about exams.",
                "history": []
            }
        )
        self.assertEqual(mental_res.status_code, 200)
        mental_data = mental_res.json()
        self.assertIn("reply", mental_data)
        self.assertEqual(mental_data["source"], "mental_wellness")
        self.assertEqual(mental_data["context_persistence"]["status"], "saved")
        self.assertGreaterEqual(mental_data["context_persistence"]["saved_count"], 1)

        # Step 3: Retrieve shared patient context from MongoDB repository
        shared_context = get_patient_context(self.shared_patient_id)
        self.assertGreaterEqual(len(shared_context), 2)

        sources = {item["source"] for item in shared_context}
        self.assertIn("nutrition", sources)
        self.assertIn("mental_wellness", sources)

        categories = {item["category"] for item in shared_context}
        self.assertTrue("hydration" in categories or "nutrition" in categories)
        self.assertTrue("sleep" in categories or "stress" in categories)

    def test_patient_isolation(self):
        """Verify that Patient A's chat-derived context NEVER appears in Patient B's retrieval."""
        # Patient A Nutrition chat
        res_a = client.post(
            "/api/nutrition/chat",
            json={
                "patient_id": self.patient_a,
                "message": "I skip breakfast almost every day during weekdays.",
                "history": []
            }
        )
        self.assertEqual(res_a.status_code, 200)

        # Patient B Mental Wellness chat
        res_b = client.post(
            "/api/mental-wellness/chat",
            json={
                "patient_id": self.patient_b,
                "message": "I have severe insomnia and lie awake for three hours.",
                "history": []
            }
        )
        self.assertEqual(res_b.status_code, 200)

        # Retrieve context for Patient A
        context_a = get_patient_context(self.patient_a)
        context_b = get_patient_context(self.patient_b)

        self.assertTrue(all(item["patient_id"] == self.patient_a for item in context_a))
        self.assertTrue(all(item["patient_id"] == self.patient_b for item in context_b))

        # Cross isolation assertion: zero overlap
        patient_a_ids = {item["_id"] for item in context_a}
        patient_b_ids = {item["_id"] for item in context_b}
        self.assertEqual(len(patient_a_ids.intersection(patient_b_ids)), 0)

    def test_storage_failure_resilience(self):
        """Verify that database persistence failure returns chat response with status='failed' without crashing."""
        with patch.object(
            context_persistence_service._repository,
            "save_context_items",
            side_effect=RuntimeError("MongoDB connection lost")
        ):
            res = client.post(
                "/api/nutrition/chat",
                json={
                    "patient_id": self.storage_fail_patient,
                    "message": "I drink only one glass of water daily.",
                    "history": []
                }
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()

            # Chat reply must STILL be returned to patient
            self.assertTrue(len(data["reply"]) > 0)
            # Persistence metadata must clearly indicate failure
            self.assertEqual(data["context_persistence"]["status"], "failed")
            self.assertEqual(data["context_persistence"]["saved_count"], 0)

            # Assert no sensitive database credentials or URI details in response body
            response_str = str(data)
            self.assertNotIn("mongodb://", response_str)
            self.assertNotIn("connection lost", response_str)

    def test_ccee_failure_resilience(self):
        """Verify that CCEE extraction failure returns chat response with status='failed' and skips DB insert."""
        with patch.object(
            context_persistence_service._ccee,
            "extract_context",
            side_effect=RuntimeError("Gemini API Rate Limit 429")
        ), patch.object(
            context_persistence_service._repository,
            "save_context_items"
        ) as mock_save:
            res = client.post(
                "/api/mental-wellness/chat",
                json={
                    "patient_id": self.ccee_fail_patient,
                    "message": "I feel stressed and sleep 4 hours.",
                    "history": []
                }
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()

            # Chat reply survives
            self.assertTrue(len(data["reply"]) > 0)
            self.assertEqual(data["context_persistence"]["status"], "failed")
            self.assertEqual(data["context_persistence"]["saved_count"], 0)

            # DB insert was NOT called
            mock_save.assert_not_called()

    def test_raw_conversation_privacy_audit(self):
        """Verify that stored MongoDB documents NEVER contain raw chat, prompts, or transcript keys."""
        res = client.post(
            "/api/nutrition/chat",
            json={
                "patient_id": self.privacy_patient,
                "message": "I drink one glass of water and skip lunch every day.",
                "history": []
            }
        )
        self.assertEqual(res.status_code, 200)

        docs = get_patient_context(self.privacy_patient)
        self.assertGreater(len(docs), 0)

        for doc in docs:
            for forbidden_key in FORBIDDEN_PRIVACY_KEYS:
                self.assertNotIn(
                    forbidden_key,
                    doc,
                    f"Privacy Violation: Forbidden raw chat key '{forbidden_key}' found in MongoDB document!"
                )
            # Verify only allowed fields exist
            allowed_keys = {
                "_id", "patient_id", "category", "summary",
                "source", "record_type", "value", "duration", "captured_at"
            }
            extra_keys = set(doc.keys()) - allowed_keys
            self.assertEqual(
                len(extra_keys),
                0,
                f"Unexpected non-schema keys found in MongoDB document: {extra_keys}"
            )


if __name__ == "__main__":
    unittest.main()
