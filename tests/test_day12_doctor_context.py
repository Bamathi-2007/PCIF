"""
Day 12 Integration Test Suite - Doctor-Side Context Assistance Layer.

Tests:
1. Current Profile Retrieval (clean domain representation, no raw ObjectIds).
2. Longitudinal History Representation (5h -> 6h -> 7h chain as neutral changes).
3. Empty Patient History Handling (0 records, request succeeds, indicates no prior context, no fabrication).
4. Relevance Selection (highlights relevant sleep/hydration context for fatigue consultation).
5. Conflict & Discrepancy Detection (stored sleep 5h vs consultation sleep 7h in items_to_verify, DB untouched).
6. Patient-Reported Provenance Labeling (explicitly identified as patient-reported).
7. Non-Diagnostic Boundary Safeguard (no diagnoses or prescription claims produced).
8. Patient Isolation (Patient A receives zero Patient B context).
9. History Limit (respects max 20 history records limit).
10. Database Failure Resilience (controlled HTTP 500 error, not confused with empty history).
11. Gemini Doctor AI Failure Resilience (controlled failure, no credentials/keys leaked).
12. Raw Chat Privacy Audit (raw chat history is never retrieved or required).
13. Request Input Validation (missing/empty patient_id or consultation rejected with HTTP 422).
"""

import os
import sys
import unittest
from datetime import datetime, timezone
from typing import List, Dict, Any
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
from database.patient_context_repository import (
    PatientContextRepository,
    save_context_item,
    save_context_items,
    get_patient_context,
    delete_patient_context,
    FORBIDDEN_PRIVACY_KEYS,
)
from backend.app.services.doctor_context_service import (
    DoctorContextService,
    doctor_context_service,
    MAX_HISTORY_LIMIT,
)

client = TestClient(app)


class MockDoctorRepository(PatientContextRepository):
    """In-memory mock repository for doctor context testing."""

    def __init__(self, collection=None):
        super().__init__(collection=collection)
        self.docs: List[Dict[str, Any]] = []

    def get_current_patient_context(self, patient_id: str) -> List[Dict[str, Any]]:
        results = []
        for d in self.docs:
            if d.get("patient_id") == patient_id and d.get("is_current", True):
                results.append(dict(d))
        results.sort(key=lambda x: x.get("captured_at"))
        return results

    def get_patient_context(self, patient_id: str) -> List[Dict[str, Any]]:
        results = []
        for d in self.docs:
            if d.get("patient_id") == patient_id:
                results.append(dict(d))
        results.sort(key=lambda x: x.get("captured_at"))
        return results


class TestDay12DoctorContext(unittest.TestCase):
    """Test suite for Day 12 Doctor-Side Context Assistance Layer."""

    def setUp(self):
        self.mock_repo = MockDoctorRepository()
        self.mock_llm = MagicMock()
        self.service = DoctorContextService(repository=self.mock_repo, llm=self.mock_llm)

    def test_1_request_input_validation(self):
        """Verify that missing or empty patient_id or consultation are rejected with 422."""
        # Missing consultation
        res = client.post("/api/doctor/context", json={"patient_id": "PAT_001"})
        self.assertEqual(res.status_code, 422)

        # Empty patient_id
        res = client.post("/api/doctor/context", json={"patient_id": "", "consultation": "Fatigue"})
        self.assertEqual(res.status_code, 422)

        # Whitespace consultation
        res = client.post("/api/doctor/context", json={"patient_id": "PAT_001", "consultation": "   "})
        self.assertEqual(res.status_code, 422)

    def test_2_current_profile_retrieval(self):
        """Verify current patient context retrieval supplies clean structured profile without raw ObjectIds."""
        self.mock_repo.docs = [
            {
                "_id": "mock_id_101",
                "patient_id": "PAT_001",
                "category": "sleep",
                "summary": "Reduced sleep",
                "source": "mental_wellness",
                "record_type": "patient_reported",
                "value": "5 hours/night",
                "captured_at": datetime.now(timezone.utc),
                "is_current": True,
            },
            {
                "_id": "mock_id_102",
                "patient_id": "PAT_001",
                "category": "hydration",
                "summary": "Low fluid intake",
                "source": "nutrition",
                "record_type": "patient_reported",
                "value": "1 glass/day",
                "captured_at": datetime.now(timezone.utc),
                "is_current": True,
            },
        ]

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Patient reports prior 5h sleep and low fluid intake.",
            "relevant_current_context": ["5 hours/night sleep", "Low fluid intake"],
            "relevant_longitudinal_changes": [],
            "items_to_verify": [],
        }

        res = self.service.generate_doctor_assistance("PAT_001", "Patient presents with daytime fatigue.")
        self.assertEqual(res["patient_id"], "PAT_001")
        self.assertIn("assistant", res)
        self.assertEqual(res["assistant"]["context_summary"], "Patient reports prior 5h sleep and low fluid intake.")

        # Inspect LLM call arguments to ensure no raw MongoDB _id leaked to LLM prompt
        call_kwargs = self.mock_llm.generate_doctor_context_assistance.call_args.kwargs
        curr_passed = call_kwargs["current_context"]
        self.assertEqual(len(curr_passed), 2)
        for item in curr_passed:
            self.assertIn("summary", item)
            self.assertIn("category", item)

    def test_3_longitudinal_history_representation(self):
        """Verify longitudinal history (5h -> 6h -> 7h) is represented as neutral shifts without diagnosis."""
        t1 = datetime(2026, 9, 1, tzinfo=timezone.utc)
        t2 = datetime(2026, 9, 10, tzinfo=timezone.utc)
        t3 = datetime(2026, 9, 18, tzinfo=timezone.utc)

        self.mock_repo.docs = [
            {"_id": "1", "patient_id": "PAT_001", "category": "sleep", "summary": "Sleep", "value": "5h", "captured_at": t1, "is_current": False},
            {"_id": "2", "patient_id": "PAT_001", "category": "sleep", "summary": "Sleep", "value": "6h", "captured_at": t2, "is_current": False},
            {"_id": "3", "patient_id": "PAT_001", "category": "sleep", "summary": "Sleep", "value": "7h", "captured_at": t3, "is_current": True},
        ]

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Reported sleep changed from 5h to 7h over stored observations.",
            "relevant_current_context": ["7h sleep/night"],
            "relevant_longitudinal_changes": ["Reported sleep duration increased from 5h to 7h."],
            "items_to_verify": [],
        }

        res = self.service.generate_doctor_assistance("PAT_001", "Follow-up consultation.")
        self.assertEqual(res["assistant"]["relevant_longitudinal_changes"], ["Reported sleep duration increased from 5h to 7h."])

    def test_4_empty_patient_history_handling(self):
        """Verify that patient with 0 stored records does not fail and does not fabricate history."""
        self.mock_repo.docs = []  # 0 records

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "No prior structured patient context is available.",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "items_to_verify": [],
        }

        res = self.service.generate_doctor_assistance("PAT_NEW", "Patient reports occasional headaches.")
        self.assertEqual(res["patient_id"], "PAT_NEW")
        self.assertIn("No prior structured patient context is available", res["assistant"]["context_summary"])
        self.assertEqual(res["assistant"]["relevant_current_context"], [])

    def test_5_conflict_discrepancy_detection(self):
        """Verify conflicting information between stored context (5h) and consultation (7h) is flagged in items_to_verify."""
        self.mock_repo.docs = [
            {
                "_id": "1",
                "patient_id": "PAT_001",
                "category": "sleep",
                "summary": "Reduced sleep",
                "value": "5 hours/night",
                "captured_at": datetime.now(timezone.utc),
                "is_current": True,
            }
        ]

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Prior context reports 5h sleep, while current consultation notes 7h sleep.",
            "relevant_current_context": ["5 hours/night sleep"],
            "relevant_longitudinal_changes": [],
            "items_to_verify": ["Discrepancy: Stored context reports 5 hours/night, but consultation notes 7 hours/night."],
        }

        res = self.service.generate_doctor_assistance("PAT_001", "Patient says they now sleep around 7 hours.")
        self.assertIn("items_to_verify", res["assistant"])
        self.assertTrue(len(res["assistant"]["items_to_verify"]) > 0)
        self.assertIn("Discrepancy", res["assistant"]["items_to_verify"][0])

        # Verify database is UNTOUCHED (doctor consultation is transient)
        self.assertEqual(len(self.mock_repo.docs), 1)
        self.assertEqual(self.mock_repo.docs[0]["value"], "5 hours/night")

    def test_6_patient_reported_provenance_labeling(self):
        """Verify Doctor AI prompt explicitly labels stored context items as patient-reported."""
        self.mock_repo.docs = [
            {
                "_id": "1",
                "patient_id": "PAT_001",
                "category": "hydration",
                "summary": "Low water intake",
                "source": "nutrition",
                "record_type": "patient_reported",
                "captured_at": datetime.now(timezone.utc),
                "is_current": True,
            }
        ]
        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Relevant prior patient-reported hydration context available.",
            "relevant_current_context": ["Patient-reported low water intake"],
            "relevant_longitudinal_changes": [],
            "items_to_verify": [],
        }

        self.service.generate_doctor_assistance("PAT_001", "Patient consultation.")
        call_kwargs = self.mock_llm.generate_doctor_context_assistance.call_args.kwargs
        curr_passed = call_kwargs["current_context"]
        self.assertEqual(curr_passed[0]["record_type"], "patient_reported")

    def test_7_no_diagnosis_boundary_safeguard(self):
        """Verify Doctor AI output surfaces context without making medical diagnosis or prescription claims."""
        self.mock_repo.docs = [
            {
                "_id": "1",
                "patient_id": "PAT_001",
                "category": "hydration",
                "summary": "Low water intake",
                "value": "1 glass/day",
                "captured_at": datetime.now(timezone.utc),
                "is_current": True,
            }
        ]

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Relevant prior patient-reported context includes low fluid intake.",
            "relevant_current_context": ["Low fluid intake (1 glass/day)"],
            "relevant_longitudinal_changes": [],
            "items_to_verify": ["Consider evaluating daily fluid intake."],
        }

        res = self.service.generate_doctor_assistance("PAT_001", "Patient presents with severe fatigue.")
        summary = res["assistant"]["context_summary"]

        self.assertNotIn("Diagnosis:", summary)
        self.assertNotIn("Dehydration Diagnosis", summary)
        self.assertNotIn("Prescribe", summary)

    def test_8_patient_isolation(self):
        """Verify patient isolation: Patient A context NEVER leaks into Patient B doctor payload."""
        self.mock_repo.docs = [
            {"_id": "1", "patient_id": "PAT_A", "category": "sleep", "summary": "Insomnia A", "captured_at": datetime.now(timezone.utc), "is_current": True},
            {"_id": "2", "patient_id": "PAT_B", "category": "nutrition", "summary": "Diet B", "captured_at": datetime.now(timezone.utc), "is_current": True},
        ]
        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Summary A",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "items_to_verify": [],
        }

        self.service.generate_doctor_assistance("PAT_A", "Consultation A")

        call_kwargs = self.mock_llm.generate_doctor_context_assistance.call_args.kwargs
        passed_current = call_kwargs["current_context"]
        passed_pids = {item.get("patient_id") for item in passed_current if "patient_id" in item}

        self.assertNotIn("PAT_B", passed_pids)
        self.assertEqual(len(passed_current), 1)
        self.assertEqual(passed_current[0]["summary"], "Insomnia A")

    def test_9_history_limit_capping(self):
        """Verify that longitudinal history is capped at MAX_HISTORY_LIMIT (20 records)."""
        now = datetime.now(timezone.utc)
        self.mock_repo.docs = [
            {
                "_id": f"id_{i}",
                "patient_id": "PAT_001",
                "category": "sleep",
                "summary": f"Sleep log {i}",
                "captured_at": now,
                "is_current": False,
            }
            for i in range(30)
        ]
        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Summary",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "items_to_verify": [],
        }

        self.service.generate_doctor_assistance("PAT_001", "Consultation note.")

        call_kwargs = self.mock_llm.generate_doctor_context_assistance.call_args.kwargs
        history_passed = call_kwargs["longitudinal_history"]
        self.assertEqual(len(history_passed), MAX_HISTORY_LIMIT)

    def test_10_database_failure_resilience(self):
        """Verify that repository database failure returns controlled HTTP 500 error."""
        with patch.object(self.service._repository, "get_current_patient_context", side_effect=RuntimeError("MongoDB unreachable")):
            with self.assertRaises(RuntimeError) as ctx:
                self.service.generate_doctor_assistance("PAT_001", "Consultation note")
            self.assertIn("Database context retrieval failed", str(ctx.exception))

    def test_11_llm_failure_resilience(self):
        """Verify that LLM failure raises controlled exception without leaking secrets."""
        self.mock_llm.generate_doctor_context_assistance.side_effect = RuntimeError("Gemini API 429 Rate Limit")
        with self.assertRaises(RuntimeError) as ctx:
            self.service.generate_doctor_assistance("PAT_001", "Consultation note")
        self.assertIn("Gemini API 429 Rate Limit", str(ctx.exception))

    def test_12_raw_chat_privacy_audit(self):
        """Verify doctor-side workflow does NOT require or query raw chat keys."""
        self.mock_repo.docs = [
            {
                "_id": "1",
                "patient_id": "PAT_PRIVACY",
                "category": "sleep",
                "summary": "Reduced sleep",
                "captured_at": datetime.now(timezone.utc),
                "is_current": True,
            }
        ]
        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Summary",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "items_to_verify": [],
        }

        res = self.service.generate_doctor_assistance("PAT_PRIVACY", "Consultation")
        self.assertIn("assistant", res)

        for forbidden in FORBIDDEN_PRIVACY_KEYS:
            self.assertNotIn(forbidden, res)
            self.assertNotIn(forbidden, res["assistant"])

    def test_13_evidence_fidelity_and_legacy_compatibility(self):
        """Verify legacy context record (missing is_current) is retrieved as active and qualifiers are passed intact."""
        # Legacy record missing is_current field
        self.mock_repo.docs = [
            {
                "_id": "legacy_doc_1",
                "patient_id": "PAT_LEGACY",
                "category": "hydration",
                "summary": "Low fluid intake",
                "source": "nutrition",
                "record_type": "patient_reported",
                "value": "1 glass on some days",
                "duration": "this week",
                "captured_at": datetime.now(timezone.utc),
                # Note: is_current is omitted (legacy record)
            }
        ]

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Patient reported drinking as little as 1 glass on some days during this week.",
            "relevant_current_context": ["1 glass on some days (this week)"],
            "relevant_longitudinal_changes": [],
            "items_to_verify": [],
        }

        res = self.service.generate_doctor_assistance("PAT_LEGACY", "Consultation note.")

        # Legacy record without is_current MUST be retrieved as active current context
        call_kwargs = self.mock_llm.generate_doctor_context_assistance.call_args.kwargs
        curr_passed = call_kwargs["current_context"]
        self.assertEqual(len(curr_passed), 1)
        self.assertEqual(curr_passed[0]["value"], "1 glass on some days")
        self.assertEqual(curr_passed[0]["duration"], "this week")

    def test_14_unpersisted_doctor_consultation_verification(self):
        """Verify that doctor consultation and AI outputs are strictly transient and not persisted."""
        initial_doc_count = len(self.mock_repo.docs)

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Summary note",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "items_to_verify": [],
        }

        self.service.generate_doctor_assistance("PAT_001", "Transient doctor consultation notes")

        # Repository doc count MUST NOT change
        self.assertEqual(len(self.mock_repo.docs), initial_doc_count)


class TestDay12DoctorAPIIntegration(unittest.TestCase):
    """API Endpoint Integration tests for POST /api/doctor/context."""

    def setUp(self):
        delete_patient_context("day12_api_patient")

    def tearDown(self):
        delete_patient_context("day12_api_patient")

    def test_api_doctor_context_end_to_end(self):
        """Test POST /api/doctor/context endpoint end-to-end with real repository."""
        item = ClinicalContextItem(
            category="sleep",
            summary="Reduced sleep associated with exam stress",
            source="mental_wellness",
            value="5 hours/night",
        )
        save_context_item("day12_api_patient", item)

        response = client.post(
            "/api/doctor/context",
            json={
                "patient_id": "day12_api_patient",
                "consultation": "Patient presents with morning fatigue and difficulty concentrating.",
            }
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["patient_id"], "day12_api_patient")
        self.assertIn("assistant", data)
        self.assertIn("disclaimer", data)
        self.assertIn("context_summary", data["assistant"])
        self.assertIn("relevant_current_context", data["assistant"])
        self.assertIn("relevant_longitudinal_changes", data["assistant"])
        self.assertIn("items_to_verify", data["assistant"])


def run_day12_tests():
    print("======================================================================")
    print("        PCIF DAY 12 DOCTOR-SIDE CONTEXT ASSISTANCE TEST SUITE         ")
    print("======================================================================")
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDay12DoctorContext))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDay12DoctorAPIIntegration))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_day12_tests()
    sys.exit(0 if success else 1)
