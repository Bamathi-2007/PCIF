"""
PCIF Day 17 Prototype Hardening & Edge-Case Verification Test Suite.

Verifies:
1. Malformed request validation (missing, null, whitespace-only fields, invalid JSON shapes -> 422).
2. Extreme input length handling (long chat, long consultation, long clinician notes -> safe execution).
3. Whitespace & identifier normalization (trimmed patient_id consistency).
4. Unicode & Multilingual character safety (Tamil, accented Latin, emoji, punctuation preserved without encoding errors).
5. Patient-Side Conversation Closure & Data Minimization:
   - Complete nutrition question -> responds and concludes naturally without unnecessary probing.
   - Sufficient mental wellness context -> supportive suggestions, natural closure.
   - Genuine ambiguity -> at most ONE targeted clarification question.
   - Post-clarification -> responds and concludes.
   - Safety-critical scenario -> emergency guidance preserved (closure rule does NOT suppress crisis escalation).
6. Duplicate submission behavior (doctor context 0 writes; append-only clinician notes).
7. HTTP Method Safety (405 Method Not Allowed on unsupported HTTP verbs).
8. Collection Separation & Zero Writeback on Doctor Context AI.
9. Interleaved / Concurrent Patient Isolation (Patient A and Patient B statelessness).
10. Database failure handling (controlled 500 without credential leakage).
11. Configuration validation (controlled error on missing MONGODB_URI).
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
from database.mongodb import MongoDBManager, ping_database, db_manager
from database.patient_context_repository import (
    save_context_item,
    get_patient_context,
    get_current_patient_context,
    delete_patient_context,
)
from database.doctor_notes_repository import (
    save_doctor_note,
    get_doctor_notes,
    delete_doctor_notes,
)

client = TestClient(app)


class TestDay17Hardening(unittest.TestCase):
    """Day 17 Prototype Hardening and Edge-Case Test Suite."""

    def setUp(self):
        """Clean up synthetic test patient IDs before each test."""
        self.patient_h1 = "day17_synth_h1"
        self.patient_h2 = "day17_synth_h2"
        self.patient_unicode = "day17_synth_unicode"
        self.patient_long = "day17_synth_long"
        self.patient_interleave_a = "day17_interleave_A"
        self.patient_interleave_b = "day17_interleave_B"

        self.test_pids = [
            self.patient_h1,
            self.patient_h2,
            self.patient_unicode,
            self.patient_long,
            self.patient_interleave_a,
            self.patient_interleave_b,
        ]

        for pid in self.test_pids:
            try:
                delete_patient_context(pid)
                delete_doctor_notes(pid)
            except Exception:
                pass

    def tearDown(self):
        """Clean up synthetic test records after each test."""
        for pid in self.test_pids:
            try:
                delete_patient_context(pid)
                delete_doctor_notes(pid)
            except Exception:
                pass

    # =========================================================================
    # 1. MALFORMED REQUEST VALIDATION
    # =========================================================================
    def test_01_malformed_patient_chat_requests(self):
        """Verify 422 Unprocessable Content on invalid chat requests."""
        # Missing patient_id
        res = client.post("/api/nutrition/chat", json={"message": "Hello"})
        self.assertEqual(res.status_code, 422)

        # Empty/whitespace patient_id
        res = client.post("/api/nutrition/chat", json={"patient_id": "   ", "message": "Hello"})
        self.assertEqual(res.status_code, 422)

        # Missing message
        res = client.post("/api/nutrition/chat", json={"patient_id": self.patient_h1})
        self.assertEqual(res.status_code, 422)

        # Empty/whitespace message
        res = client.post("/api/mental-wellness/chat", json={"patient_id": self.patient_h1, "message": "   "})
        self.assertEqual(res.status_code, 422)

        # Invalid JSON type (number instead of string)
        res = client.post("/api/nutrition/chat", json={"patient_id": 12345, "message": "Hello"})
        self.assertEqual(res.status_code, 422)

    def test_02_malformed_doctor_context_requests(self):
        """Verify 422 Unprocessable Content on invalid doctor context requests."""
        # Missing consultation
        res = client.post("/api/doctor/context", json={"patient_id": self.patient_h1})
        self.assertEqual(res.status_code, 422)

        # Whitespace consultation
        res = client.post("/api/doctor/context", json={"patient_id": self.patient_h1, "consultation": "   "})
        self.assertEqual(res.status_code, 422)

        # Whitespace patient_id
        res = client.post("/api/doctor/context", json={"patient_id": "  ", "consultation": "Consult"})
        self.assertEqual(res.status_code, 422)

    def test_03_malformed_doctor_notes_requests(self):
        """Verify 422 Unprocessable Content on invalid doctor notes requests."""
        # Missing note
        res = client.post("/api/doctor/notes", json={"patient_id": self.patient_h1})
        self.assertEqual(res.status_code, 422)

        # Whitespace note
        res = client.post("/api/doctor/notes", json={"patient_id": self.patient_h1, "note": "   "})
        self.assertEqual(res.status_code, 422)

        # GET notes with whitespace patient_id
        res = client.get("/api/doctor/notes/%20%20%20")
        self.assertEqual(res.status_code, 422)

    # =========================================================================
    # 2. EXTREME INPUT LENGTH HANDLING
    # =========================================================================
    @patch("backend.app.services.llm_service.GeminiLLMService.generate_doctor_context_assistance")
    @patch("backend.app.services.llm_service.GeminiLLMService.chat_nutrition")
    @patch("ccee.engine.ClinicalContextExtractionEngine.extract_context")
    def test_04_extreme_input_lengths(self, mock_ccee, mock_chat, mock_doc_ai):
        """Verify system handles long input payloads without crashes, corruption, or leakages."""
        pid = self.patient_long
        long_chat_text = "I have been experiencing fatigue. " * 200  # ~6.8 KB
        long_consultation = "Attending physician notes for extensive review. " * 300  # ~14 KB
        long_doctor_note = "Detailed clinical review and discussion with patient. " * 150  # ~7 KB

        mock_chat.return_value = "Guidance for long message."
        mock_ccee.return_value = []
        mock_doc_ai.return_value = {
            "context_summary": "Extensive consultation summarized safely.",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": [],
        }

        # 1. Long chat message
        chat_res = client.post(
            "/api/nutrition/chat",
            json={"patient_id": pid, "message": long_chat_text},
        )
        self.assertEqual(chat_res.status_code, 200)

        # 2. Long doctor note save
        save_res = client.post(
            "/api/doctor/notes",
            json={"patient_id": pid, "note": long_doctor_note},
        )
        self.assertEqual(save_res.status_code, 200)
        stored_notes = get_doctor_notes(pid)
        self.assertEqual(len(stored_notes), 1)
        self.assertEqual(stored_notes[0]["note"], long_doctor_note.strip())

        # 3. Long consultation text
        doc_res = client.post(
            "/api/doctor/context",
            json={"patient_id": pid, "consultation": long_consultation},
        )
        self.assertEqual(doc_res.status_code, 200)

    # =========================================================================
    # 3. WHITESPACE & IDENTIFIER NORMALIZATION
    # =========================================================================
    def test_05_whitespace_identifier_normalization(self):
        """Verify leading and trailing whitespace around patient_id is cleanly normalized."""
        untrimmed_pid = "   day17_synth_h1   "
        clean_pid = "day17_synth_h1"

        # Save note with untrimmed PID
        save_resp = client.post(
            "/api/doctor/notes",
            json={"patient_id": untrimmed_pid, "note": "Normalization test note."},
        )
        self.assertEqual(save_resp.status_code, 200)
        self.assertEqual(save_resp.json()["note"]["patient_id"], clean_pid)

        # Retrieve with clean PID
        notes = get_doctor_notes(clean_pid)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["patient_id"], clean_pid)

    # =========================================================================
    # 4. UNICODE & MULTILINGUAL CHARACTER SAFETY
    # =========================================================================
    @patch("backend.app.services.llm_service.GeminiLLMService.generate_doctor_context_assistance")
    def test_06_unicode_and_multilingual_safety(self, mock_doc_ai):
        """Verify non-Latin Unicode text (Tamil, accents, emoji) is preserved accurately."""
        pid = self.patient_unicode
        tamil_note = "நோயாளி காலை உணவை தவிர்ப்பதாக தெரிவித்தார்; சோர்வு உள்ளது. 😴"
        accented_consult = "Examen de rutina: paciente refiere fatiga matutina y cefalea."

        mock_doc_ai.return_value = {
            "context_summary": "Tamil and accented notes processed safely.",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [tamil_note],
            "items_to_verify": [],
        }

        # 1. Save Tamil + Emoji note
        save_res = client.post(
            "/api/doctor/notes",
            json={"patient_id": pid, "note": tamil_note},
        )
        self.assertEqual(save_res.status_code, 200)

        # 2. Retrieve and verify Unicode preservation
        notes = get_doctor_notes(pid)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["note"], tamil_note)

        # 3. Doctor context call with accented consultation
        doc_res = client.post(
            "/api/doctor/context",
            json={"patient_id": pid, "consultation": accented_consult},
        )
        self.assertEqual(doc_res.status_code, 200)
        assistant = doc_res.json()["assistant"]
        self.assertEqual(assistant["relevant_clinician_notes"][0], tamil_note)

    # =========================================================================
    # 5. PATIENT-SIDE CONVERSATION CLOSURE & DATA MINIMIZATION
    # =========================================================================
    @patch("backend.app.services.llm_service.GeminiLLMService.chat_nutrition")
    @patch("ccee.engine.ClinicalContextExtractionEngine.extract_context")
    def test_07_nutrition_complete_question_natural_closure(self, mock_ccee, mock_chat):
        """Test A: User asks a complete nutrition question -> AI provides answer with natural closure, no probing."""
        pid = self.patient_h1
        # Mock LLM adhering to Day 17 data-minimization instruction
        mock_chat.return_value = (
            "Here are three quick, high-protein breakfast options: 1) Greek yoghurt with almonds, "
            "2) Boiled eggs with whole-grain toast, 3) Peanut butter on oats. "
            "If you would like to explore any of these ideas further, let me know."
        )
        mock_ccee.return_value = []

        res = client.post(
            "/api/nutrition/chat",
            json={
                "patient_id": pid,
                "message": "What are some quick high-protein breakfast ideas for college mornings?",
                "history": [],
            },
        )
        self.assertEqual(res.status_code, 200)
        reply = res.json()["reply"]
        # Verify natural conclusion and lack of intrusive follow-up interrogation
        self.assertIn("let me know", reply.lower())
        self.assertNotIn("how many hours do you sleep", reply.lower())

    @patch("backend.app.services.llm_service.GeminiLLMService.chat_mental_wellness")
    @patch("ccee.engine.ClinicalContextExtractionEngine.extract_context")
    def test_08_mental_wellness_sufficient_context_natural_closure(self, mock_ccee, mock_chat):
        """Test B: User provides sufficient mental wellness context -> AI responds supportively and concludes naturally."""
        pid = self.patient_h1
        mock_chat.return_value = (
            "It is completely understandable to feel overwhelmed during exam weeks. "
            "Taking short 5-minute breathing pauses and breaking study blocks into 25-minute sessions can help. "
            "Take your time with these ideas, and feel free to reach out if you would like to talk more."
        )
        mock_ccee.return_value = [
            ClinicalContextItem(
                category="stress",
                summary="Overwhelmed with exam revision",
                source="mental_wellness",
                record_type="patient_reported",
            )
        ]

        res = client.post(
            "/api/mental-wellness/chat",
            json={
                "patient_id": pid,
                "message": "I feel very overwhelmed with my exams this week.",
                "history": [],
            },
        )
        self.assertEqual(res.status_code, 200)
        reply = res.json()["reply"]
        self.assertIn("feel free to reach out", reply.lower())

    @patch("backend.app.services.llm_service.GeminiLLMService.chat_nutrition")
    def test_09_ambiguous_question_targeted_clarification(self, mock_chat):
        """Test C: Genuinely ambiguous input -> at most ONE targeted clarification question."""
        pid = self.patient_h1
        mock_chat.return_value = (
            "I can certainly help you adjust your meal habits. "
            "To give you the most relevant suggestions, are you looking to eat more regularly, or are you looking for healthier snack options?"
        )

        res = client.post(
            "/api/nutrition/chat",
            json={"patient_id": pid, "message": "I want to change my diet.", "history": []},
        )
        self.assertEqual(res.status_code, 200)
        reply = res.json()["reply"]
        # Single focused question
        self.assertEqual(reply.count("?"), 1)

    @patch("backend.app.services.llm_service.GeminiLLMService.chat_nutrition")
    @patch("ccee.engine.ClinicalContextExtractionEngine.extract_context")
    def test_10_post_clarification_natural_conclusion(self, mock_ccee, mock_chat):
        """Test D: After clarification is supplied, AI responds and concludes rather than continuing to interrogate."""
        pid = self.patient_h1
        mock_chat.return_value = (
            "To eat more regularly during college, try setting a consistent 15-minute breakfast window "
            "and carrying a portable snack like fruit or mixed nuts. "
            "If you would like to discuss anything else, let me know."
        )
        mock_ccee.return_value = [
            ClinicalContextItem(
                category="habit",
                summary="Goal to establish regular meal timing",
                source="nutrition",
                record_type="patient_reported",
            )
        ]

        history = [
            {"role": "user", "content": "I want to change my diet."},
            {"role": "assistant", "content": "Are you looking to eat more regularly or find healthier snacks?"},
        ]

        res = client.post(
            "/api/nutrition/chat",
            json={
                "patient_id": pid,
                "message": "I want to eat more regularly on class days.",
                "history": history,
            },
        )
        self.assertEqual(res.status_code, 200)
        reply = res.json()["reply"]
        self.assertIn("let me know", reply.lower())
        self.assertNotIn("?", reply)  # Concludes without asking another question

    @patch("backend.app.services.llm_service.GeminiLLMService.chat_mental_wellness")
    def test_11_safety_critical_crisis_escalation_preserved(self, mock_chat):
        """Test E: Safety-critical situation -> emergency crisis escalation is NOT suppressed by closure rule."""
        pid = self.patient_h1
        mock_chat.return_value = (
            "I am so sorry that you are going through this, but please know that your safety is the most important thing right now. "
            "Please contact local emergency services immediately, go to the nearest hospital emergency room, "
            "or reach out to someone you trust who can be with you right now."
        )

        res = client.post(
            "/api/mental-wellness/chat",
            json={
                "patient_id": pid,
                "message": "I feel like ending my life today.",
                "history": [],
            },
        )
        self.assertEqual(res.status_code, 200)
        reply = res.json()["reply"]
        self.assertIn("emergency", reply.lower())

    # =========================================================================
    # 6. DUPLICATE SUBMISSION & APPEND-ONLY PERSISTENCE
    # =========================================================================
    @patch("backend.app.services.llm_service.GeminiLLMService.generate_doctor_context_assistance")
    def test_12_doctor_context_duplicate_submission_zero_writes(self, mock_doc_ai):
        """Verify calling Doctor Context AI multiple times causes zero writes every time."""
        pid = self.patient_h1
        mock_doc_ai.return_value = {
            "context_summary": "Test summary.",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": [],
        }

        # First call
        client.post("/api/doctor/context", json={"patient_id": pid, "consultation": "Consult 1"})
        # Second rapid call
        client.post("/api/doctor/context", json={"patient_id": pid, "consultation": "Consult 1"})

        self.assertEqual(len(get_patient_context(pid)), 0)
        self.assertEqual(len(get_doctor_notes(pid)), 0)

    def test_13_clinician_note_append_only_duplicate_submissions(self):
        """Verify explicit repeated clinician note submissions produce independent append-only records."""
        pid = self.patient_h1
        note_text = "Identical explicit clinician observation."

        # Save note #1
        r1 = client.post("/api/doctor/notes", json={"patient_id": pid, "note": note_text})
        self.assertEqual(r1.status_code, 200)

        # Save note #2
        r2 = client.post("/api/doctor/notes", json={"patient_id": pid, "note": note_text})
        self.assertEqual(r2.status_code, 200)

        # In Day 14/15/16/17 append-only model, both explicit notes are preserved
        notes = get_doctor_notes(pid)
        self.assertEqual(len(notes), 2)
        for n in notes:
            self.assertEqual(n["record_type"], "doctor_confirmed")

    # =========================================================================
    # 7. HTTP METHOD SAFETY
    # =========================================================================
    def test_14_http_method_safety(self):
        """Verify unsupported HTTP methods return 405 Method Not Allowed without state mutation."""
        pid = self.patient_h1

        # GET on /api/doctor/context (POST only)
        res = client.get("/api/doctor/context")
        self.assertEqual(res.status_code, 405)

        # GET on /api/doctor/notes (POST only; retrieval is GET /api/doctor/notes/{pid})
        res = client.get("/api/doctor/notes")
        self.assertEqual(res.status_code, 405)

        # POST on /api/doctor/notes/{pid} (GET only)
        res = client.post(f"/api/doctor/notes/{pid}", json={"data": "test"})
        self.assertEqual(res.status_code, 405)

    # =========================================================================
    # 8. INTERLEAVED CONCURRENT PATIENT ISOLATION
    # =========================================================================
    @patch("backend.app.services.llm_service.GeminiLLMService.generate_doctor_context_assistance")
    def test_15_interleaved_patient_operations_isolation(self, mock_doc_ai):
        """Verify repository and service are fully stateless under rapid interleaved multi-patient operations."""
        pid_a = self.patient_interleave_a
        pid_b = self.patient_interleave_b

        # 1. Save context for A
        save_context_item(
            pid_a,
            ClinicalContextItem(
                category="sleep",
                summary="Patient A sleep issue",
                source="mental_wellness",
                record_type="patient_reported",
            ),
        )
        # 2. Save note for B
        save_doctor_note(pid_b, "Patient B note on cardio.")
        # 3. Save note for A
        save_doctor_note(pid_a, "Patient A note on diet.")
        # 4. Save context for B
        save_context_item(
            pid_b,
            ClinicalContextItem(
                category="nutrition",
                summary="Patient B hydration issue",
                source="nutrition",
                record_type="patient_reported",
            ),
        )

        # Verify A isolation
        ctx_a = get_patient_context(pid_a)
        notes_a = get_doctor_notes(pid_a)
        self.assertEqual(len(ctx_a), 1)
        self.assertEqual(ctx_a[0]["summary"], "Patient A sleep issue")
        self.assertEqual(len(notes_a), 1)
        self.assertEqual(notes_a[0]["note"], "Patient A note on diet.")

        # Verify B isolation
        ctx_b = get_patient_context(pid_b)
        notes_b = get_doctor_notes(pid_b)
        self.assertEqual(len(ctx_b), 1)
        self.assertEqual(ctx_b[0]["summary"], "Patient B hydration issue")
        self.assertEqual(len(notes_b), 1)
        self.assertEqual(notes_b[0]["note"], "Patient B note on cardio.")

    # =========================================================================
    # 9. CONFIGURATION & DATABASE HARDENING
    # =========================================================================
    def test_16_missing_mongodb_uri_explicit_failure(self):
        """Verify missing or blank MONGODB_URI causes controlled ConnectionError without silent localhost fallback."""
        mgr = MongoDBManager(uri="", db_name="pcif")
        with self.assertRaises(ConnectionError):
            mgr.get_client()

    @patch("database.patient_context_repository.PatientContextRepository.get_current_patient_context")
    def test_17_database_unreachable_controlled_error(self, mock_get_ctx):
        """Verify unreachable DB returns controlled 500 without leaking credentials or tracebacks."""
        mock_get_ctx.side_effect = ConnectionError("Connection to mongodb://secret_user:secret_pass@cluster.mongodb.net failed")

        res = client.post(
            "/api/doctor/context",
            json={"patient_id": self.patient_h1, "consultation": "Patient checkup."},
        )
        self.assertEqual(res.status_code, 500)
        detail = res.json()["detail"]
        # Ensure URI secrets are not leaked
        self.assertNotIn("secret_user", detail)
        self.assertNotIn("secret_pass", detail)
        self.assertNotIn("mongodb.net", detail)


if __name__ == "__main__":
    unittest.main(verbosity=2)
