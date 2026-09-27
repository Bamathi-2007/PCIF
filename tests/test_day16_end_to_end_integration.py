"""
PCIF Day 16 End-to-End Integration & Defect Hardening Test Suite.

Proves that Days 1-15 operate correctly as ONE complete system.
Uses strictly synthetic patient scenarios and synthetic data.

Verified Lifecycles & Invariants:
1. Complete E2E Lifecycle: Patient Nutrition + Mental Wellness -> CCEE -> patient_context
   -> Doctor Context AI -> Clinician Note Save -> Second Doctor Context AI with 3 sources.
2. Raw Chat Privacy Audit: Zero forbidden conversational/chat keys stored in MongoDB.
3. Shared Patient ID: Nutrition and Mental Wellness co-exist under same patient_id with intact sources.
4. Longitudinal Update Scenario: Changing patient report (5h -> 7h sleep) updates active record while preserving history.
5. Distinct Context Coexistence: Different context categories remain independently active (no over-consolidation).
6. First Doctor Context Request: Correct behavior when clinician history is empty (relevant_clinician_notes = []).
7. Doctor Response Shape & Boundaries: Strict assistive format with zero diagnostic/prescriptive fields.
8. Clinician Note Save & Separation: doctor_notes receives record; patient_context untouched.
9. Human Authoring Boundary & No Writeback: Zero database mutations caused by Doctor Context AI calls.
10. Patient Isolation End-to-End: Complete isolation between Patient A and Patient B across all channels.
11. Source Provenance Isolation: source="nutrition" vs source="mental_wellness" strictly preserved.
12. Empty Patient End-to-End: Unknown patient processes current consultation without hallucinating history.
13. Irrelevant Patient Chat: Non-clinical input returns no_relevant_context, 0 DB writes, chat intact.
14. CCEE Failure vs Irrelevance: Infrastructure failure handled safely and distinguished from empty context.
15. Database Failure Paths: Controlled HTTP 500 on DB errors (never masked as fake empty success).
16. Gemini Failure Path: Controlled HTTP 500 on LLM error with zero DB mutations.
17. Collection Separation Invariants: Direct verification of complete isolation between collections.
18. Live MongoDB Connectivity: Live DB ping and collection health verification.
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
from database.mongodb import ping_database, db_manager
from database.patient_context_repository import (
    PatientContextRepository,
    save_context_item,
    get_patient_context,
    get_current_patient_context,
    delete_patient_context,
    FORBIDDEN_PRIVACY_KEYS,
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


class TestDay16EndToEndIntegration(unittest.TestCase):
    """Day 16 End-to-End PCIF Integration Test Suite."""

    def setUp(self):
        """Clean up synthetic patient test IDs before each test."""
        self.patient_primary = "e2e_synth_patient_001"
        self.patient_a = "e2e_synth_patient_A"
        self.patient_b = "e2e_synth_patient_B"
        self.patient_empty = "e2e_synth_patient_empty"
        self.patient_irrelevant = "e2e_synth_patient_irrel"
        self.patient_ccee_fail = "e2e_synth_patient_ccee_fail"
        self.patient_db_fail = "e2e_synth_patient_db_fail"

        self.all_test_pids = [
            self.patient_primary,
            self.patient_a,
            self.patient_b,
            self.patient_empty,
            self.patient_irrelevant,
            self.patient_ccee_fail,
            self.patient_db_fail,
        ]

        for pid in self.all_test_pids:
            try:
                delete_patient_context(pid)
                delete_doctor_notes(pid)
            except Exception:
                pass

    def tearDown(self):
        """Clean up synthetic test records after each test."""
        for pid in self.all_test_pids:
            try:
                delete_patient_context(pid)
                delete_doctor_notes(pid)
            except Exception:
                pass

    # =========================================================================
    # 1. PRIMARY COMPLETE END-TO-END LIFECYCLE
    # =========================================================================
    @patch("backend.app.services.llm_service.GeminiLLMService.generate_doctor_context_assistance")
    @patch("backend.app.services.llm_service.GeminiLLMService.chat_mental_wellness")
    @patch("backend.app.services.llm_service.GeminiLLMService.chat_nutrition")
    @patch("ccee.engine.ClinicalContextExtractionEngine.extract_context")
    def test_01_primary_end_to_end_lifecycle(
        self, mock_ccee, mock_chat_nutr, mock_chat_mw, mock_doc_ai
    ):
        """
        Full PCIF Lifecycle:
        Step 1: Patient Nutrition AI interaction -> CCEE -> patient_context
        Step 2: Patient Mental Wellness AI interaction -> CCEE -> patient_context
        Step 3: First Doctor Context Request -> Retrieves patient context + empty clinician notes
        Step 4: Clinician manually authors & saves note -> doctor_notes
        Step 5: Second Doctor Context Request -> Retrieves patient context + clinician note history
        """
        pid = self.patient_primary
        mock_chat_nutr.return_value = "It is important to have regular breakfasts and stay hydrated."
        mock_chat_mw.return_value = "Exam stress can significantly impact your sleep quality."

        # -------------------------------------------------------------
        # Step 1: Patient Nutrition Interaction
        # -------------------------------------------------------------
        mock_ccee.return_value = [
            ClinicalContextItem(
                category="nutrition",
                summary="Skips breakfast on most college days",
                value="most college days",
                duration="this week",
                source="nutrition",
                record_type="patient_reported",
            ),
            ClinicalContextItem(
                category="hydration",
                summary="Reports low daily water intake",
                value="very little water",
                duration="this week",
                source="nutrition",
                record_type="patient_reported",
            ),
        ]

        nutr_resp = client.post(
            "/api/nutrition/chat",
            json={
                "patient_id": pid,
                "message": "I've been skipping breakfast most college days this week and drinking very little water.",
                "history": [],
            },
        )
        self.assertEqual(nutr_resp.status_code, 200)
        self.assertEqual(nutr_resp.json()["status"], "success")
        self.assertEqual(nutr_resp.json()["context_persistence"]["status"], "saved")
        self.assertEqual(nutr_resp.json()["context_persistence"]["saved_count"], 2)

        # -------------------------------------------------------------
        # Step 2: Patient Mental Wellness Interaction
        # -------------------------------------------------------------
        mock_ccee.return_value = [
            ClinicalContextItem(
                category="sleep",
                summary="Sleep duration approximately 5 hours per night due to exam stress",
                value="5 hours/night",
                duration="this week",
                source="mental_wellness",
                record_type="patient_reported",
            )
        ]

        mw_resp = client.post(
            "/api/mental-wellness/chat",
            json={
                "patient_id": pid,
                "message": "I've been sleeping around five hours a night this week because of exam stress.",
                "history": [],
            },
        )
        self.assertEqual(mw_resp.status_code, 200)
        self.assertEqual(mw_resp.json()["status"], "success")
        self.assertEqual(mw_resp.json()["context_persistence"]["status"], "saved")

        # Verify patient_context in DB contains all 3 items under same patient_id
        stored_items = get_patient_context(pid)
        self.assertEqual(len(stored_items), 3)
        sources = {item.get("source") for item in stored_items}
        self.assertEqual(sources, {"nutrition", "mental_wellness"})
        for item in stored_items:
            self.assertEqual(item.get("record_type"), "patient_reported")

        # -------------------------------------------------------------
        # Step 3: First Doctor Context Request (0 clinician notes)
        # -------------------------------------------------------------
        mock_doc_ai.return_value = {
            "context_summary": "Patient-reported context notes meal skipping, low hydration, and reduced sleep (~5h/night) during exams.",
            "relevant_current_context": [
                "Skips breakfast on most college days (nutrition)",
                "Low water intake (hydration)",
                "Sleep duration ~5 hours/night (sleep)",
            ],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": ["Confirm current fluid intake and exam timeline."],
        }

        doc_req_1 = client.post(
            "/api/doctor/context",
            json={
                "patient_id": pid,
                "consultation": "Patient reports morning fatigue and difficulty concentrating.",
            },
        )
        self.assertEqual(doc_req_1.status_code, 200)
        res_1 = doc_req_1.json()
        self.assertIn("assistant", res_1)
        self.assertEqual(res_1["assistant"]["relevant_clinician_notes"], [])
        self.assertIn("disclaimer", res_1)

        # -------------------------------------------------------------
        # Step 4: Clinician Manually Authors & Saves Note
        # -------------------------------------------------------------
        save_note_resp = client.post(
            "/api/doctor/notes",
            json={
                "patient_id": pid,
                "note": "Reviewed current sleep pattern and fatigue during consultation; sleep duration and hydration discussed.",
            },
        )
        self.assertEqual(save_note_resp.status_code, 200)
        note_data = save_note_resp.json()["note"]
        self.assertEqual(note_data["record_type"], "doctor_confirmed")
        self.assertEqual(note_data["patient_id"], pid)

        # Verify collection isolation: patient_context unchanged, doctor_notes has 1
        self.assertEqual(len(get_patient_context(pid)), 3)
        doc_notes_stored = get_doctor_notes(pid)
        self.assertEqual(len(doc_notes_stored), 1)
        self.assertEqual(doc_notes_stored[0]["record_type"], "doctor_confirmed")

        # -------------------------------------------------------------
        # Step 5: Second Doctor Context Request (with clinician note)
        # -------------------------------------------------------------
        mock_doc_ai.return_value = {
            "context_summary": "Patient reports fatigue. Prior clinician-authored note reviewed sleep patterns. Patient context shows ongoing exam stress and low sleep.",
            "relevant_current_context": [
                "Sleep duration ~5 hours/night (sleep)",
                "Low water intake (hydration)",
            ],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [
                "Reviewed current sleep pattern and fatigue during consultation; sleep duration and hydration discussed."
            ],
            "items_to_verify": ["Assess progress on hydration and sleep since previous consultation."],
        }

        doc_req_2 = client.post(
            "/api/doctor/context",
            json={
                "patient_id": pid,
                "consultation": "Patient returns for follow-up regarding persistent fatigue.",
            },
        )
        self.assertEqual(doc_req_2.status_code, 200)
        res_2 = doc_req_2.json()
        self.assertEqual(len(res_2["assistant"]["relevant_clinician_notes"]), 1)
        self.assertIn("Reviewed current sleep pattern", res_2["assistant"]["relevant_clinician_notes"][0])

    # =========================================================================
    # 2. RAW CHAT PRIVACY AUDIT
    # =========================================================================
    def test_02_raw_chat_privacy_audit(self):
        """Verify that zero raw chat keys exist in patient_context or doctor_notes."""
        pid = self.patient_primary
        # Seed synthetic patient context & doctor note
        save_context_item(
            pid,
            ClinicalContextItem(
                category="sleep",
                summary="Sleep duration ~5 hours",
                value="5h",
                source="mental_wellness",
                record_type="patient_reported",
            ),
        )
        save_doctor_note(pid, "Clinician review note.")

        ctx_records = get_patient_context(pid)
        note_records = get_doctor_notes(pid)

        for rec in ctx_records:
            for forbidden_key in FORBIDDEN_PRIVACY_KEYS:
                self.assertNotIn(
                    forbidden_key,
                    rec,
                    f"Forbidden key '{forbidden_key}' found in patient_context record: {rec}",
                )

        for rec in note_records:
            for forbidden_key in ["messages", "history", "conversation", "raw_chat", "full_transcript", "prompt"]:
                self.assertNotIn(
                    forbidden_key,
                    rec,
                    f"Forbidden key '{forbidden_key}' found in doctor_notes record: {rec}",
                )

    # =========================================================================
    # 3. SHARED PATIENT ID & SOURCE PRESERVATION
    # =========================================================================
    def test_03_shared_patient_id_multi_source(self):
        """Verify Nutrition and Mental Wellness records coexist under same patient_id with preserved sources."""
        pid = self.patient_primary

        save_context_item(
            pid,
            ClinicalContextItem(
                category="nutrition",
                summary="Skips breakfast on weekdays",
                source="nutrition",
                record_type="patient_reported",
            ),
        )
        save_context_item(
            pid,
            ClinicalContextItem(
                category="stress",
                summary="Elevated academic stress",
                source="mental_wellness",
                record_type="patient_reported",
            ),
        )

        records = get_patient_context(pid)
        self.assertEqual(len(records), 2)
        by_cat = {r["category"]: r for r in records}
        self.assertEqual(by_cat["nutrition"]["source"], "nutrition")
        self.assertEqual(by_cat["stress"]["source"], "mental_wellness")
        self.assertEqual(by_cat["nutrition"]["record_type"], "patient_reported")
        self.assertEqual(by_cat["stress"]["record_type"], "patient_reported")

    # =========================================================================
    # 4. LONGITUDINAL UPDATE SCENARIO
    # =========================================================================
    @patch("backend.app.services.llm_service.GeminiLLMService.classify_longitudinal_relation")
    def test_04_longitudinal_update_scenario(self, mock_classify):
        """Verify longitudinal update: previous sleep becomes superseded, new sleep becomes active current."""
        pid = self.patient_primary
        from backend.app.services.longitudinal_context_service import longitudinal_context_service

        # Initial report: 5 hours sleep
        item1 = ClinicalContextItem(
            category="sleep",
            summary="Sleep duration 5 hours/night",
            value="5 hours/night",
            duration="1 week",
            source="mental_wellness",
            record_type="patient_reported",
        )
        res1 = longitudinal_context_service.save_longitudinal_context(pid, [item1])
        self.assertEqual(res1.inserted_count, 1)

        # Later report: 7 hours sleep (classified as update)
        mock_classify.return_value = "update"
        item2 = ClinicalContextItem(
            category="sleep",
            summary="Sleep duration increased to 7 hours/night",
            value="7 hours/night",
            duration="past 3 days",
            source="mental_wellness",
            record_type="patient_reported",
        )
        res2 = longitudinal_context_service.save_longitudinal_context(pid, [item2])
        self.assertEqual(res2.inserted_count, 1)
        self.assertEqual(res2.superseded_count, 1)

        # get_patient_context returns all history (2 records)
        all_records = get_patient_context(pid)
        self.assertEqual(len(all_records), 2)

        # get_current_patient_context returns only current active record (1 record: 7h)
        current_records = get_current_patient_context(pid)
        self.assertEqual(len(current_records), 1)
        self.assertEqual(current_records[0]["value"], "7 hours/night")
        self.assertTrue(current_records[0]["is_current"])

    # =========================================================================
    # 5. DISTINCT CONTEXT COEXISTENCE
    # =========================================================================
    @patch("backend.app.services.llm_service.GeminiLLMService.classify_longitudinal_relation")
    def test_05_distinct_context_coexistence(self, mock_classify):
        """Verify truly distinct items remain independently current (no false consolidation)."""
        pid = self.patient_primary
        from backend.app.services.longitudinal_context_service import longitudinal_context_service

        mock_classify.return_value = "distinct"

        item_nutr = ClinicalContextItem(
            category="nutrition",
            summary="Skips breakfast on weekdays",
            source="nutrition",
            record_type="patient_reported",
        )
        item_hydr = ClinicalContextItem(
            category="hydration",
            summary="Low water intake",
            source="nutrition",
            record_type="patient_reported",
        )
        item_sleep = ClinicalContextItem(
            category="sleep",
            summary="Sleep duration 5h/night",
            source="mental_wellness",
            record_type="patient_reported",
        )

        longitudinal_context_service.save_longitudinal_context(pid, [item_nutr, item_hydr, item_sleep])

        current_items = get_current_patient_context(pid)
        self.assertEqual(len(current_items), 3)
        for item in current_items:
            self.assertTrue(item.get("is_current"))

    # =========================================================================
    # 6. DOCTOR RESPONSE SHAPE & BOUNDARIES
    # =========================================================================
    @patch("backend.app.services.llm_service.GeminiLLMService.generate_doctor_context_assistance")
    def test_06_doctor_response_shape_and_boundaries(self, mock_doc_ai):
        """Verify response contains all required fields and ZERO forbidden diagnostic/treatment fields."""
        pid = self.patient_primary
        mock_doc_ai.return_value = {
            "context_summary": "Patient reports morning fatigue. Prior context notes 5 hours sleep.",
            "relevant_current_context": ["Sleep duration 5h/night (patient-reported)"],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": ["Confirm sleep duration."],
        }

        resp = client.post(
            "/api/doctor/context",
            json={"patient_id": pid, "consultation": "Patient reports morning fatigue."},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertIn("patient_id", data)
        self.assertIn("assistant", data)
        self.assertIn("disclaimer", data)

        assistant = data["assistant"]
        self.assertIn("context_summary", assistant)
        self.assertIn("relevant_current_context", assistant)
        self.assertIn("relevant_longitudinal_changes", assistant)
        self.assertIn("relevant_clinician_notes", assistant)
        self.assertIn("items_to_verify", assistant)

        forbidden_output_fields = [
            "diagnosis",
            "treatment_plan",
            "risk_score",
            "disease_probability",
            "medication_recommendation",
            "prescriptions",
            "icd_code",
        ]
        for field in forbidden_output_fields:
            self.assertNotIn(field, assistant)
            self.assertNotIn(field, data)

    # =========================================================================
    # 7. CLINICIAN NOTE SAVE & COLLECTION SEPARATION
    # =========================================================================
    def test_07_clinician_note_save_and_separation(self):
        """Verify saving clinician note writes ONLY to doctor_notes with record_type='doctor_confirmed'."""
        pid = self.patient_primary
        save_context_item(
            pid,
            ClinicalContextItem(
                category="sleep",
                summary="5h sleep",
                source="mental_wellness",
                record_type="patient_reported",
            ),
        )

        ctx_count_before = len(get_patient_context(pid))
        notes_count_before = len(get_doctor_notes(pid))

        resp = client.post(
            "/api/doctor/notes",
            json={"patient_id": pid, "note": "Clinician personally reviewed sleep complaints."},
        )
        self.assertEqual(resp.status_code, 200)

        ctx_count_after = len(get_patient_context(pid))
        notes_count_after = len(get_doctor_notes(pid))

        self.assertEqual(ctx_count_after, ctx_count_before)
        self.assertEqual(notes_count_after, notes_count_before + 1)

    # =========================================================================
    # 8. HUMAN AUTHORING BOUNDARY & NO WRITEBACK
    # =========================================================================
    @patch("backend.app.services.llm_service.GeminiLLMService.generate_doctor_context_assistance")
    def test_08_human_authoring_boundary_and_no_writeback(self, mock_doc_ai):
        """Verify Doctor Context AI call causes ZERO writes to patient_context or doctor_notes."""
        pid = self.patient_primary
        save_context_item(
            pid,
            ClinicalContextItem(
                category="sleep",
                summary="5h sleep",
                source="mental_wellness",
                record_type="patient_reported",
            ),
        )
        save_doctor_note(pid, "Historical clinician note.")

        mock_doc_ai.return_value = {
            "context_summary": "Summary of context.",
            "relevant_current_context": ["5h sleep"],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": ["Historical clinician note."],
            "items_to_verify": [],
        }

        ctx_before = len(get_patient_context(pid))
        notes_before = len(get_doctor_notes(pid))

        client.post(
            "/api/doctor/context",
            json={"patient_id": pid, "consultation": "Patient reports tiredness."},
        )

        ctx_after = len(get_patient_context(pid))
        notes_after = len(get_doctor_notes(pid))

        self.assertEqual(ctx_before, ctx_after)
        self.assertEqual(notes_before, notes_after)

    # =========================================================================
    # 9. PATIENT ISOLATION END-TO-END
    # =========================================================================
    @patch("backend.app.services.llm_service.GeminiLLMService.generate_doctor_context_assistance")
    def test_09_patient_isolation_end_to_end(self, mock_doc_ai):
        """Verify Patient A records never leak into Patient B doctor context calls or data."""
        pid_a = self.patient_a
        pid_b = self.patient_b

        # Seed Patient A
        save_context_item(
            pid_a,
            ClinicalContextItem(
                category="nutrition",
                summary="Patient A skips breakfast",
                source="nutrition",
                record_type="patient_reported",
            ),
        )
        save_doctor_note(pid_a, "Patient A clinician note regarding breakfast.")

        # Seed Patient B
        save_context_item(
            pid_b,
            ClinicalContextItem(
                category="stress",
                summary="Patient B severe work stress",
                source="mental_wellness",
                record_type="patient_reported",
            ),
        )
        save_doctor_note(pid_b, "Patient B clinician note regarding stress.")

        captured_calls = []

        def side_effect(*args, **kwargs):
            captured_calls.append(kwargs)
            return {
                "context_summary": "Isolated summary.",
                "relevant_current_context": [],
                "relevant_longitudinal_changes": [],
                "relevant_clinician_notes": [],
                "items_to_verify": [],
            }

        mock_doc_ai.side_effect = side_effect

        # Call for Patient A
        resp_a = client.post("/api/doctor/context", json={"patient_id": pid_a, "consultation": "Consult A"})
        self.assertEqual(resp_a.status_code, 200)
        self.assertTrue(len(captured_calls) >= 1)
        call_a = captured_calls[-1]

        # Verify Patient A call contains ONLY Patient A data
        ctx_a_str = str(call_a.get("current_context", [])) + str(call_a.get("clinician_notes", []))
        self.assertIn("Patient A", ctx_a_str)
        self.assertNotIn("Patient B", ctx_a_str)

        # Call for Patient B
        resp_b = client.post("/api/doctor/context", json={"patient_id": pid_b, "consultation": "Consult B"})
        self.assertEqual(resp_b.status_code, 200)
        self.assertTrue(len(captured_calls) >= 2)
        call_b = captured_calls[-1]

        # Verify Patient B call contains ONLY Patient B data
        ctx_b_str = str(call_b.get("current_context", [])) + str(call_b.get("clinician_notes", []))
        self.assertIn("Patient B", ctx_b_str)
        self.assertNotIn("Patient A", ctx_b_str)

    # =========================================================================
    # 10. SOURCE PROVENANCE ISOLATION
    # =========================================================================
    def test_10_source_provenance_isolation(self):
        """Verify source field is immutable and strictly preserved across queries."""
        pid = self.patient_primary

        save_context_item(
            pid,
            ClinicalContextItem(
                category="sleep",
                summary="Nutrition-related sleep impact",
                source="nutrition",
                record_type="patient_reported",
            ),
        )
        save_context_item(
            pid,
            ClinicalContextItem(
                category="sleep",
                summary="Stress-related sleep impact",
                source="mental_wellness",
                record_type="patient_reported",
            ),
        )

        records = get_patient_context(pid)
        self.assertEqual(len(records), 2)
        sources = [r["source"] for r in records]
        self.assertIn("nutrition", sources)
        self.assertIn("mental_wellness", sources)

    # =========================================================================
    # 11. EMPTY PATIENT END-TO-END
    # =========================================================================
    @patch("backend.app.services.llm_service.GeminiLLMService.generate_doctor_context_assistance")
    def test_11_empty_patient_end_to_end(self, mock_doc_ai):
        """Verify completely unknown patient with 0 records succeeds without fabricating history."""
        pid = self.patient_empty
        mock_doc_ai.return_value = {
            "context_summary": "No prior structured patient-reported context or clinician-authored notes on record.",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": [],
        }

        resp = client.post(
            "/api/doctor/context",
            json={"patient_id": pid, "consultation": "New patient first visit consultation."},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["assistant"]["relevant_current_context"], [])
        self.assertEqual(data["assistant"]["relevant_clinician_notes"], [])

    # =========================================================================
    # 12. IRRELEVANT PATIENT CHAT
    # =========================================================================
    @patch("ccee.engine.ClinicalContextExtractionEngine.extract_context")
    @patch("backend.app.services.llm_service.GeminiLLMService.chat_nutrition")
    def test_12_irrelevant_patient_chat(self, mock_chat, mock_ccee):
        """Verify non-clinical patient chat produces no_relevant_context, 0 DB writes, chat intact."""
        pid = self.patient_irrelevant
        mock_chat.return_value = "Hello! I am here to help you with nutrition and lifestyle guidance."
        mock_ccee.return_value = []  # No clinical context extracted

        resp = client.post(
            "/api/nutrition/chat",
            json={"patient_id": pid, "message": "Hello, what is your favorite color?", "history": []},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["context_persistence"]["status"], "no_relevant_context")
        self.assertEqual(data["context_persistence"]["saved_count"], 0)

        self.assertEqual(len(get_patient_context(pid)), 0)

    # =========================================================================
    # 13. CCEE FAILURE VS IRRELEVANCE
    # =========================================================================
    @patch("ccee.engine.ClinicalContextExtractionEngine.extract_context")
    @patch("backend.app.services.llm_service.GeminiLLMService.chat_nutrition")
    def test_13_ccee_failure_vs_irrelevance(self, mock_chat, mock_ccee):
        """Verify CCEE exception returns context_persistence.status='failed' while preserving chat response."""
        pid = self.patient_ccee_fail
        mock_chat.return_value = "Here is some helpful nutrition advice."
        mock_ccee.side_effect = RuntimeError("CCEE API timeout error")

        resp = client.post(
            "/api/nutrition/chat",
            json={"patient_id": pid, "message": "I eat lunch very late.", "history": []},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["context_persistence"]["status"], "failed")
        self.assertEqual(data["context_persistence"]["saved_count"], 0)

        # 0 DB writes
        self.assertEqual(len(get_patient_context(pid)), 0)

    # =========================================================================
    # 14. DATABASE FAILURE PATHS
    # =========================================================================
    @patch("database.patient_context_repository.PatientContextRepository.get_current_patient_context")
    def test_14_patient_context_db_failure(self, mock_get_ctx):
        """Verify patient_context DB failure raises controlled HTTP 500 (never fake empty success)."""
        pid = self.patient_db_fail
        mock_get_ctx.side_effect = ConnectionError("MongoDB unreachable")

        resp = client.post(
            "/api/doctor/context",
            json={"patient_id": pid, "consultation": "Patient consult."},
        )
        self.assertEqual(resp.status_code, 500)
        self.assertIn("error occurred", resp.json()["detail"].lower())

    @patch("database.doctor_notes_repository.DoctorNotesRepository.get_doctor_notes")
    def test_15_doctor_notes_retrieval_db_failure(self, mock_get_notes):
        """Verify doctor_notes retrieval DB failure raises controlled HTTP 500 (never fake empty notes)."""
        pid = self.patient_db_fail
        mock_get_notes.side_effect = ConnectionError("doctor_notes connection lost")

        resp = client.post(
            "/api/doctor/context",
            json={"patient_id": pid, "consultation": "Patient consult."},
        )
        self.assertEqual(resp.status_code, 500)
        self.assertIn("error occurred", resp.json()["detail"].lower())

    @patch("database.doctor_notes_repository.DoctorNotesRepository.save_doctor_note")
    def test_16_doctor_notes_write_db_failure(self, mock_save_note):
        """Verify doctor_notes write DB failure raises controlled HTTP 500."""
        pid = self.patient_db_fail
        mock_save_note.side_effect = RuntimeError("Disk full / write failure")

        resp = client.post(
            "/api/doctor/notes",
            json={"patient_id": pid, "note": "Doctor note text."},
        )
        self.assertEqual(resp.status_code, 500)
        self.assertIn("error occurred", resp.json()["detail"].lower())

    # =========================================================================
    # 15. GEMINI FAILURE PATH
    # =========================================================================
    @patch("backend.app.services.llm_service.GeminiLLMService.generate_doctor_context_assistance")
    def test_17_doctor_context_gemini_failure(self, mock_doc_ai):
        """Verify Gemini LLM failure raises controlled HTTP 500 without mutating DB."""
        pid = self.patient_primary
        mock_doc_ai.side_effect = RuntimeError("Gemini API rate limit 429")

        resp = client.post(
            "/api/doctor/context",
            json={"patient_id": pid, "consultation": "Patient consult."},
        )
        self.assertEqual(resp.status_code, 500)

        # DB remains 0
        self.assertEqual(len(get_patient_context(pid)), 0)
        self.assertEqual(len(get_doctor_notes(pid)), 0)

    # =========================================================================
    # 16. COLLECTION SEPARATION INVARIANTS
    # =========================================================================
    def test_18_collection_separation_invariants(self):
        """Verify saving to patient_context never writes doctor_notes, and saving to doctor_notes never writes patient_context."""
        pid = self.patient_primary

        # 1. Save patient context
        save_context_item(
            pid,
            ClinicalContextItem(
                category="nutrition",
                summary="Breakfast skipping",
                source="nutrition",
                record_type="patient_reported",
            ),
        )
        self.assertEqual(len(get_patient_context(pid)), 1)
        self.assertEqual(len(get_doctor_notes(pid)), 0)

        # 2. Save doctor note
        save_doctor_note(pid, "Clinician review note.")
        self.assertEqual(len(get_patient_context(pid)), 1)
        self.assertEqual(len(get_doctor_notes(pid)), 1)

    # =========================================================================
    # 17. LIVE MONGODB CONNECTIVITY
    # =========================================================================
    def test_19_live_mongodb_ping_and_status(self):
        """Verify live MongoDB connection ping and status reporting."""
        is_alive = ping_database()
        self.assertTrue(is_alive, "Live MongoDB connection failed ping.")

        status = db_manager.get_status()
        self.assertTrue(status["connected"])
        self.assertEqual(status["status"], "connected")
        self.assertIn("patient_context", status["collections"])
        self.assertIn("doctor_notes", status["collections"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
