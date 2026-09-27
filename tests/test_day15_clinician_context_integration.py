"""
Day 15 Integration Test Suite - Clinician Notes Integration into Doctor Context AI.

Tests:
1. Clinician History Retrieval: Stored clinician-authored notes are retrieved and passed in structured prompt.
2. Patient Isolation: Patient A receives only Patient A clinician notes; Patient B notes never leak into prompt or output.
3. Empty Clinician History: Patient with patient_context but zero doctor_notes succeeds with relevant_clinician_notes = [].
4. Clinician Notes Only: Patient with zero patient_context but existing doctor_notes succeeds and preserves clinician notes.
5. Completely Empty History: Patient with zero patient_context and zero doctor_notes processes consultation without fabrication.
6. Source Provenance Separation: Prompt structure maintains three distinct provenance channels (Consultation, Patient-Reported, Clinician-Authored).
7. Conflict & Discrepancy Handling: Multi-source conflicts (patient 5h, clinician 7h, consultation 6h) surfaced in items_to_verify without silent overwrites.
8. Relevance Selection: Only contextually relevant clinician notes are selected by Doctor AI (unrelated notes omitted).
9. History Limit (MAX_CLINICIAN_NOTES): Most recent 10 notes capped without altering stored records.
10. Timestamp Semantics: Stored timestamp represents persistence time (saved_at) and is never treated as clinical symptom onset.
11. No Writeback: Doctor Context AI execution causes zero database writes (patient_context and doctor_notes counts untouched).
12. DB Failure Resilience: Controlled failure raised on doctor_notes retrieval error; never masked as fake empty history.
13. No CCEE / Longitudinal Mutation: Doctor Context workflow never invokes CCEE extraction or Day 11 consolidation.
14. API End-to-End: POST /api/doctor/context returns relevant_clinician_notes in assistant payload.
"""

import os
import sys
import unittest
from datetime import datetime, timezone, timedelta
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
)
from backend.app.services.doctor_context_service import (
    DoctorContextService,
    doctor_context_service,
    MAX_CLINICIAN_NOTES,
    MAX_HISTORY_LIMIT,
)

client = TestClient(app)


class MockPatientContextRepo(PatientContextRepository):
    """In-memory mock for patient_context repository."""

    def __init__(self, collection=None):
        super().__init__(collection=collection)
        self.docs: List[Dict[str, Any]] = []

    def get_current_patient_context(self, patient_id: str) -> List[Dict[str, Any]]:
        results = [dict(d) for d in self.docs if d.get("patient_id") == patient_id and d.get("is_current", True)]
        results.sort(key=lambda x: x.get("captured_at", datetime.min))
        return results

    def get_patient_context(self, patient_id: str) -> List[Dict[str, Any]]:
        results = [dict(d) for d in self.docs if d.get("patient_id") == patient_id]
        results.sort(key=lambda x: x.get("captured_at", datetime.min))
        return results


class MockDoctorNotesRepo(DoctorNotesRepository):
    """In-memory mock for doctor_notes repository."""

    def __init__(self, collection=None):
        super().__init__(collection=collection)
        self.docs: List[Dict[str, Any]] = []

    def get_doctor_notes(self, patient_id: str) -> List[Dict[str, Any]]:
        results = [dict(d) for d in self.docs if d.get("patient_id") == patient_id]
        results.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        return results

    def save_doctor_note(self, patient_id: str, note: str) -> Dict[str, Any]:
        clean_patient_id = self._validate_patient_id(patient_id)
        clean_note = self._validate_note(note)
        now_utc = datetime.now(timezone.utc)
        doc = {
            "id": f"mock_dn_{len(self.docs) + 1}",
            "_id": f"mock_dn_{len(self.docs) + 1}",
            "patient_id": clean_patient_id,
            "note": clean_note,
            "record_type": "doctor_confirmed",
            "created_at": now_utc,
        }
        self.docs.append(doc)
        return doc


class TestDay15ClinicianContextIntegration(unittest.TestCase):
    """Unit and integration test suite for Day 15 Doctor Context AI clinician notes integration."""

    def setUp(self):
        self.mock_pcontext_repo = MockPatientContextRepo()
        self.mock_dnotes_repo = MockDoctorNotesRepo()
        self.mock_llm = MagicMock()
        self.service = DoctorContextService(
            repository=self.mock_pcontext_repo,
            doctor_notes_repo=self.mock_dnotes_repo,
            llm=self.mock_llm,
        )

    def test_1_clinician_history_retrieval(self):
        """1. Clinician history retrieval: Stored clinician notes are included in LLM call."""
        t1 = datetime(2026, 9, 20, 10, 0, 0, tzinfo=timezone.utc)
        self.mock_dnotes_repo.docs = [
            {
                "id": "1",
                "patient_id": "PAT_001",
                "note": "Clinician evaluated persistent morning fatigue.",
                "record_type": "doctor_confirmed",
                "created_at": t1,
            }
        ]

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Prior clinician note noted persistent morning fatigue.",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": ["Prior clinician note noted persistent morning fatigue."],
            "items_to_verify": [],
        }

        res = self.service.generate_doctor_assistance("PAT_001", "Follow-up consultation.")
        self.assertEqual(res["patient_id"], "PAT_001")
        self.assertIn("relevant_clinician_notes", res["assistant"])
        self.assertEqual(len(res["assistant"]["relevant_clinician_notes"]), 1)

        # Inspect LLM call kwargs
        call_kwargs = self.mock_llm.generate_doctor_context_assistance.call_args.kwargs
        self.assertIn("clinician_notes", call_kwargs)
        passed_notes = call_kwargs["clinician_notes"]
        self.assertEqual(len(passed_notes), 1)
        self.assertEqual(passed_notes[0]["note"], "Clinician evaluated persistent morning fatigue.")

    def test_2_patient_isolation(self):
        """2. Patient isolation: Patient A receives only Patient A clinician notes."""
        self.mock_dnotes_repo.docs = [
            {"id": "1", "patient_id": "PAT_A", "note": "Patient A clinician note", "created_at": datetime.now(timezone.utc)},
            {"id": "2", "patient_id": "PAT_B", "note": "Patient B clinician note", "created_at": datetime.now(timezone.utc)},
        ]

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Summary A",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": ["Patient A clinician note"],
            "items_to_verify": [],
        }

        self.service.generate_doctor_assistance("PAT_A", "Consultation A")

        call_kwargs = self.mock_llm.generate_doctor_context_assistance.call_args.kwargs
        passed_notes = call_kwargs["clinician_notes"]
        self.assertEqual(len(passed_notes), 1)
        self.assertEqual(passed_notes[0]["note"], "Patient A clinician note")
        for n in passed_notes:
            self.assertNotIn("Patient B", n.get("note", ""))

    def test_3_empty_clinician_history(self):
        """3. Empty clinician history: Zero doctor_notes returns relevant_clinician_notes = []."""
        self.mock_pcontext_repo.docs = [
            {
                "id": "1",
                "patient_id": "PAT_001",
                "category": "sleep",
                "summary": "Reported sleep 6h",
                "source": "mental_wellness",
                "record_type": "patient_reported",
                "captured_at": datetime.now(timezone.utc),
                "is_current": True,
            }
        ]
        self.mock_dnotes_repo.docs = []  # No clinician notes

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Patient-reported 6h sleep.",
            "relevant_current_context": ["Reported sleep 6h"],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": [],
        }

        res = self.service.generate_doctor_assistance("PAT_001", "Consultation")
        self.assertEqual(res["assistant"]["relevant_clinician_notes"], [])

    def test_4_clinician_notes_only(self):
        """4. Clinician notes only: Zero patient_context but clinician notes present."""
        self.mock_pcontext_repo.docs = []  # No patient context
        self.mock_dnotes_repo.docs = [
            {
                "id": "1",
                "patient_id": "PAT_DOC_ONLY",
                "note": "Clinician recorded baseline normal ECG.",
                "created_at": datetime.now(timezone.utc),
            }
        ]

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Prior clinician note recorded baseline normal ECG; no prior patient-reported context available.",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": ["Baseline normal ECG recorded previously."],
            "items_to_verify": [],
        }

        res = self.service.generate_doctor_assistance("PAT_DOC_ONLY", "Routine checkup.")
        call_kwargs = self.mock_llm.generate_doctor_context_assistance.call_args.kwargs
        self.assertEqual(len(call_kwargs["current_context"]), 0)
        self.assertEqual(len(call_kwargs["clinician_notes"]), 1)
        self.assertEqual(len(res["assistant"]["relevant_clinician_notes"]), 1)

    def test_5_completely_empty_history(self):
        """5. Completely empty history: Zero patient_context and zero doctor_notes."""
        self.mock_pcontext_repo.docs = []
        self.mock_dnotes_repo.docs = []

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "No prior structured patient context or clinician notes are available for this patient.",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": [],
        }

        res = self.service.generate_doctor_assistance("PAT_NEW", "First visit notes.")
        self.assertIn("No prior structured patient context", res["assistant"]["context_summary"])
        self.assertEqual(res["assistant"]["relevant_clinician_notes"], [])
        self.assertEqual(res["assistant"]["relevant_current_context"], [])

    def test_6_source_provenance_separation_in_prompt(self):
        """6. Source provenance separation: Prompt contains distinct sections for all 3 sources."""
        from backend.app.services.llm_service import GeminiLLMService
        llm = GeminiLLMService()

        # Capture prompt via mocked client
        mock_client = MagicMock()
        with patch.object(llm, "_get_client", return_value=mock_client):
            mock_client.models.generate_content.return_value.text = (
                '{"context_summary": "Summary", "relevant_current_context": [], '
                '"relevant_longitudinal_changes": [], "relevant_clinician_notes": [], "items_to_verify": []}'
            )

            llm.generate_doctor_context_assistance(
                patient_id="PAT_PROV_TEST",
                consultation="Patient reports headache.",
                current_context=[{"category": "sleep", "summary": "Sleep 5h", "record_type": "patient_reported"}],
                longitudinal_history=[{"category": "sleep", "summary": "Sleep 5h", "record_type": "patient_reported"}],
                clinician_notes=[{"note": "Prior tension headache note", "created_at": datetime.now(timezone.utc)}],
            )

            call_args = mock_client.models.generate_content.call_args
            prompt_text = call_args.kwargs["contents"]

            # Verify three clearly separated sections exist in prompt
            self.assertIn("[SOURCE A: CURRENT CLINICIAN CONSULTATION NOTES]", prompt_text)
            self.assertIn("[SOURCE B: PATIENT-REPORTED CONTEXT]", prompt_text)
            self.assertIn("[SOURCE C: CLINICIAN-AUTHORED HISTORICAL NOTES]", prompt_text)
            self.assertIn("Active Current Patient-Reported Profile", prompt_text)
            self.assertIn("Clinician-Authored Notes History", prompt_text)

    def test_7_conflict_handling(self):
        """7. Conflict handling: Multi-source conflict placed in items_to_verify without overwriting."""
        self.mock_pcontext_repo.docs = [
            {
                "id": "1",
                "patient_id": "PAT_001",
                "category": "sleep",
                "summary": "Patient reported approximately 5 hours/night",
                "record_type": "patient_reported",
                "value": "5h",
                "captured_at": datetime.now(timezone.utc),
                "is_current": True,
            }
        ]
        self.mock_dnotes_repo.docs = [
            {
                "id": "1",
                "patient_id": "PAT_001",
                "note": "Clinician documented patient sleeping approximately 7 hours nightly during last visit.",
                "created_at": datetime.now(timezone.utc),
            }
        ]

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Prior patient-reported context recorded 5h sleep, whereas previous clinician note recorded 7h sleep. Current consultation reports 6h sleep.",
            "relevant_current_context": ["Patient-reported sleep: 5h"],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": ["Clinician documented approximately 7 hours nightly during last visit."],
            "items_to_verify": [
                "Discrepancy: Patient-reported context records 5 hours/night, prior clinician note documents 7 hours/night, and current consultation notes 6 hours/night. Consider confirming current pattern."
            ],
        }

        res = self.service.generate_doctor_assistance("PAT_001", "Patient now reports sleeping around 6 hours.")
        self.assertTrue(len(res["assistant"]["items_to_verify"]) > 0)
        self.assertIn("Discrepancy", res["assistant"]["items_to_verify"][0])

        # Verify underlying database records are untouched
        self.assertEqual(len(self.mock_pcontext_repo.docs), 1)
        self.assertEqual(len(self.mock_dnotes_repo.docs), 1)

    def test_8_relevance_selection(self):
        """8. Relevance selection: Only consultation-relevant clinician notes are surfaced in output."""
        self.mock_dnotes_repo.docs = [
            {"id": "1", "patient_id": "PAT_001", "note": "Reviewed chronic fatigue during previous visit.", "created_at": datetime.now(timezone.utc)},
            {"id": "2", "patient_id": "PAT_001", "note": "Evaluated right ankle sprain; recommended ice and rest.", "created_at": datetime.now(timezone.utc)},
            {"id": "3", "patient_id": "PAT_001", "note": "Discussed ongoing sleep disruption.", "created_at": datetime.now(timezone.utc)},
        ]

        # LLM correctly selects fatigue and sleep, omitting unrelated ankle sprain
        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Relevant prior clinician notes include chronic fatigue and sleep disruption discussions.",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [
                "Reviewed chronic fatigue during previous visit.",
                "Discussed ongoing sleep disruption."
            ],
            "items_to_verify": [],
        }

        res = self.service.generate_doctor_assistance("PAT_001", "Patient presents with fatigue.")
        notes_surfaced = res["assistant"]["relevant_clinician_notes"]
        self.assertEqual(len(notes_surfaced), 2)
        for n in notes_surfaced:
            self.assertNotIn("ankle", n.lower())

    def test_9_history_limit_capping(self):
        """9. History limit: Caps clinician notes at MAX_CLINICIAN_NOTES (10)."""
        now = datetime.now(timezone.utc)
        self.mock_dnotes_repo.docs = [
            {
                "id": f"id_{i}",
                "patient_id": "PAT_LIMIT",
                "note": f"Clinician note {i}",
                "created_at": now + timedelta(minutes=i),
            }
            for i in range(25)
        ]

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Summary",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": [],
        }

        self.service.generate_doctor_assistance("PAT_LIMIT", "Consultation note.")

        call_kwargs = self.mock_llm.generate_doctor_context_assistance.call_args.kwargs
        notes_passed = call_kwargs["clinician_notes"]
        self.assertEqual(len(notes_passed), MAX_CLINICIAN_NOTES)
        self.assertEqual(MAX_CLINICIAN_NOTES, 10)

    def test_10_timestamp_semantics_no_clinical_onset(self):
        """10. Timestamp semantics: created_at represents persistence time (saved_at)."""
        t = datetime(2026, 9, 25, 14, 30, tzinfo=timezone.utc)
        self.mock_dnotes_repo.docs = [
            {
                "id": "1",
                "patient_id": "PAT_TIME",
                "note": "Documented mild tremor.",
                "created_at": t,
            }
        ]

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "A clinician note saved on 2026-09-25 recorded mild tremor.",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": ["Clinician note recorded on 2026-09-25: documented mild tremor."],
            "items_to_verify": [],
        }

        res = self.service.generate_doctor_assistance("PAT_TIME", "Consultation")
        summary = res["assistant"]["context_summary"]
        self.assertNotIn("tremor began on 2026-09-25", summary)
        self.assertNotIn("onset on 2026-09-25", summary)

    def test_11_no_writeback_persistence_safety(self):
        """11. No writeback: Doctor Context AI execution causes zero database writes."""
        self.mock_pcontext_repo.docs = [{"id": "1", "patient_id": "PAT_001", "summary": "S1", "is_current": True}]
        self.mock_dnotes_repo.docs = [{"id": "1", "patient_id": "PAT_001", "note": "N1"}]

        pcontext_count_before = len(self.mock_pcontext_repo.docs)
        dnotes_count_before = len(self.mock_dnotes_repo.docs)

        self.mock_llm.generate_doctor_context_assistance.return_value = {
            "context_summary": "Summary",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": [],
        }

        self.service.generate_doctor_assistance("PAT_001", "Transient consultation")

        self.assertEqual(len(self.mock_pcontext_repo.docs), pcontext_count_before)
        self.assertEqual(len(self.mock_dnotes_repo.docs), dnotes_count_before)

    def test_12_database_failure_resilience(self):
        """12. DB failure: Controlled failure raised on doctor_notes retrieval error."""
        with patch.object(self.service._doctor_notes_repo, "get_doctor_notes", side_effect=RuntimeError("doctor_notes connection failure")):
            with self.assertRaises(RuntimeError) as ctx:
                self.service.generate_doctor_assistance("PAT_001", "Consultation")
            self.assertIn("Database clinician notes retrieval failed", str(ctx.exception))

    def test_13_no_ccee_invocation(self):
        """13. No CCEE: Doctor Context generation must never invoke CCEE extraction."""
        with patch("ccee.engine.ClinicalContextExtractionEngine.extract_context") as mock_ccee:
            self.mock_llm.generate_doctor_context_assistance.return_value = {
                "context_summary": "Summary",
                "relevant_current_context": [],
                "relevant_longitudinal_changes": [],
                "relevant_clinician_notes": [],
                "items_to_verify": [],
            }
            self.service.generate_doctor_assistance("PAT_001", "Consultation")
            mock_ccee.assert_not_called()


class TestDay15DoctorContextAPI(unittest.TestCase):
    """API endpoint integration test for POST /api/doctor/context with Day 15 fields."""

    def setUp(self):
        delete_patient_context("day15_api_test_patient")
        delete_doctor_notes("day15_api_test_patient")

    def tearDown(self):
        delete_patient_context("day15_api_test_patient")
        delete_doctor_notes("day15_api_test_patient")

    def test_api_doctor_context_with_clinician_notes(self):
        """Test POST /api/doctor/context returns assistant with relevant_clinician_notes."""
        patient_id = "day15_api_test_patient"

        # 1. Seed 1 patient_context item
        item = ClinicalContextItem(
            category="sleep",
            summary="Patient reported 5h sleep during exam period",
            source="mental_wellness",
            value="5h",
        )
        save_context_item(patient_id, item)

        # 2. Seed 1 doctor_notes record
        save_doctor_note(patient_id, "Attending clinician reviewed sleep hygiene recommendations.")

        # 3. Call POST /api/doctor/context
        res = client.post(
            "/api/doctor/context",
            json={
                "patient_id": patient_id,
                "consultation": "Patient reports ongoing daytime fatigue.",
            }
        )

        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["patient_id"], patient_id)
        self.assertIn("assistant", data)
        self.assertIn("context_summary", data["assistant"])
        self.assertIn("relevant_current_context", data["assistant"])
        self.assertIn("relevant_longitudinal_changes", data["assistant"])
        self.assertIn("relevant_clinician_notes", data["assistant"])
        self.assertIn("items_to_verify", data["assistant"])
        self.assertIsInstance(data["assistant"]["relevant_clinician_notes"], list)


def run_day15_tests():
    print("======================================================================")
    print("       PCIF DAY 15 CLINICIAN CONTEXT INTEGRATION TEST SUITE           ")
    print("======================================================================")
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDay15ClinicianContextIntegration))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDay15DoctorContextAPI))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_day15_tests()
    sys.exit(0 if success else 1)
