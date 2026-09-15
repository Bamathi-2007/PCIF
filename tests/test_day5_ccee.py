"""
Day 5 CCEE Test Suite - Verification and Edge Cases.

Runs:
1. Local Schema, Contract, and Boundary Tests (No LLM calls)
2. Live Conservative Gemini CCEE Evaluation (Paced calls with rate-limit protection)
"""

import os
import sys
import time
import json
from typing import List, Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure utf-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from ccee.schema import (
    ClinicalContextItem,
    ALLOWED_SOURCES,
    ALLOWED_CATEGORIES,
    ALLOWED_RECORD_TYPES,
)
from ccee.engine import ClinicalContextExtractionEngine, ccee_engine
from backend.app.services.llm_service import llm_service


def run_local_contract_tests():
    print("\n" + "=" * 60)
    print("PHASE 1: LOCAL CONTRACT & BOUNDARY TESTS (NO LLM CALLS)")
    print("=" * 60)

    # 1. Valid item creation and serialization
    item = ClinicalContextItem(
        category="sleep",
        summary="Reduced sleep associated with exam stress",
        source="mental_wellness",
        record_type="patient_reported",
        value="5 hours/night",
        duration="1 week"
    )
    d = item.to_dict()
    assert d["category"] == "sleep"
    assert d["summary"] == "Reduced sleep associated with exam stress"
    assert d["source"] == "mental_wellness"
    assert d["record_type"] == "patient_reported"
    assert d["value"] == "5 hours/night"
    assert d["duration"] == "1 week"
    print("✓ Test 1 Passed: Valid ClinicalContextItem creation & serialization")

    # 2. Optional fields omitted when None or empty
    item_no_optional = ClinicalContextItem(
        category="nutrition",
        summary="Regularly skips breakfast",
        source="nutrition"
    )
    d2 = item_no_optional.to_dict()
    assert "value" not in d2
    assert "duration" not in d2
    print("✓ Test 2 Passed: Optional value/duration omitted when not provided")

    # 3. Invalid source rejection
    try:
        ClinicalContextItem(
            category="nutrition",
            summary="Skips breakfast",
            source="cardiology"
        )
        assert False, "Should have raised ValueError for invalid source"
    except ValueError as ve:
        assert "Invalid source" in str(ve)
        print("✓ Test 3 Passed: Invalid source rejected by ClinicalContextItem")

    # 4. Invalid source rejected by engine.extract_context
    try:
        ccee_engine.extract_context("I feel tired", "oncology")
        assert False, "Should have raised ValueError in engine"
    except ValueError as ve:
        assert "Invalid source" in str(ve)
        print("✓ Test 4 Passed: Invalid source rejected by engine.extract_context")

    # 5. Invalid category rejection
    try:
        ClinicalContextItem(
            category="finance",
            summary="High expenses",
            source="mental_wellness"
        )
        assert False, "Should have raised ValueError for invalid category"
    except ValueError as ve:
        assert "Invalid category" in str(ve)
        print("✓ Test 5 Passed: Invalid category rejected by ClinicalContextItem")

    # 6. Invalid record_type rejection
    try:
        ClinicalContextItem(
            category="sleep",
            summary="Slept 5 hours",
            source="mental_wellness",
            record_type="physician_diagnosed"
        )
        assert False, "Should have raised ValueError for invalid record_type"
    except ValueError as ve:
        assert "Invalid record_type" in str(ve)
        print("✓ Test 6 Passed: Invalid record_type rejected by ClinicalContextItem")

    # 7. Empty input returns [] without calling LLM
    empty_result = ccee_engine.extract_context("   ", "nutrition")
    assert empty_result == []
    print("✓ Test 7 Passed: Whitespace-only conversation immediately returns []")

    # 8. Handling of transcript lists
    transcript = [
        {"role": "user", "content": "I keep skipping breakfast."},
        {"role": "assistant", "content": "How long has that been happening?"}
    ]
    normalized = ClinicalContextExtractionEngine._normalize_conversation(transcript)
    assert "User: I keep skipping breakfast." in normalized
    assert "Assistant: How long has that been happening?" in normalized
    print("✓ Test 8 Passed: Transcript conversation turns normalized correctly")

    # 9. Graceful handling of mock malformed LLM response
    class MockFailingService:
        def extract_ccee(self, conversation_text, source):
            return [{"category": "invalid_category", "summary": "Bad item"}]

    mock_engine = ClinicalContextExtractionEngine(service=MockFailingService())
    safe_result = mock_engine.extract_context("Some text", "nutrition")
    assert safe_result == []
    print("✓ Test 9 Passed: Malformed LLM output discarded safely without crash")

    # 10. Nutrition & Mental Wellness AI chat methods still accessible
    assert hasattr(llm_service, "chat_nutrition")
    assert hasattr(llm_service, "chat_mental_wellness")
    assert callable(llm_service.chat_nutrition)
    assert callable(llm_service.chat_mental_wellness)
    print("✓ Test 10 Passed: Nutrition AI and Mental Wellness AI services intact")


def run_live_gemini_tests():
    print("\n" + "=" * 60)
    print("PHASE 2: LIVE GEMINI CCEE TESTS (CONSERVATIVE PACING)")
    print("=" * 60)

    # 5 Day 4 Frozen Test Cases
    day4_cases = [
        {
            "id": "3.1",
            "name": "Skipped breakfast due early classes",
            "source": "nutrition",
            "text": "I keep having to skip breakfast almost every morning because my college lectures start at 7:30 AM and I have to rush out.",
            "expect_empty": False,
            "expected_category": "nutrition",
        },
        {
            "id": "3.2",
            "name": "Reduced sleep due exam stress",
            "source": "mental_wellness",
            "text": "I've been sleeping around five hours because I'm stressed about exams for the last week.",
            "expect_empty": False,
            "expected_category": "sleep",
        },
        {
            "id": "3.3",
            "name": "Reduced appetite for one week",
            "source": "nutrition",
            "text": "For the past week, my appetite has dropped significantly and I feel full after eating barely half a meal.",
            "expect_empty": False,
            "expected_category": "appetite",
        },
        {
            "id": "3.4",
            "name": "Low water intake",
            "source": "nutrition",
            "text": "I barely drink any water during the day, usually just one small glass because I get busy and keep forgetting.",
            "expect_empty": False,
            "expected_category": "hydration",
        },
        {
            "id": "3.5",
            "name": "Irrelevant conversation (weather/car)",
            "source": "mental_wellness",
            "text": "Do you think it's going to rain this afternoon? I'm trying to decide if I should wash my car today or wait until the weekend.",
            "expect_empty": True,
            "expected_category": None,
        },
    ]

    # 5 Day 5 New Edge Cases
    day5_cases = [
        {
            "id": "4.1 (A)",
            "name": "Casual greeting",
            "source": "mental_wellness",
            "text": "Hi, how are you today?",
            "expect_empty": True,
            "expected_category": None,
        },
        {
            "id": "4.2 (B)",
            "name": "Preference without health relevance",
            "source": "nutrition",
            "text": "My favourite colour is yellow.",
            "expect_empty": True,
            "expected_category": None,
        },
        {
            "id": "4.3 (C)",
            "name": "Multiple meaningful phenomena",
            "source": "mental_wellness",
            "text": "I've been skipping meals this week and sleeping only four hours because I'm stressed about exams.",
            "expect_empty": False,
            "expected_category": None,  # expects multiple
        },
        {
            "id": "4.4 (D)",
            "name": "Unsupported diagnosis prevention",
            "source": "mental_wellness",
            "text": "I've been feeling tired and sleeping only four hours.",
            "expect_empty": False,
            "prohibited_words": ["insomnia", "depression", "anemia", "disorder", "syndrome", "chronic fatigue"],
        },
        {
            "id": "4.5 (E)",
            "name": "Uncertain self-report",
            "source": "nutrition",
            "text": "I think I've been eating less than usual recently.",
            "expect_empty": False,
            "prohibited_words": ["severe", "anorexia", "malnutrition", "100%", "starvation"],
        },
    ]

    results = []

    for i, case in enumerate(day4_cases + day5_cases):
        case_id = str(case["id"])
        name = str(case["name"])
        text = str(case["text"])
        source = str(case["source"])

        print(f"\nEvaluating Case {case_id}: {name}")
        print(f"  Source: {source}")
        print(f"  Input: \"{text}\"")

        # Paced delay to respect free-tier Gemini rate limits
        if i > 0:
            time.sleep(2.0)

        # Retry loop for transient 503/429 Gemini API server spikes
        max_retries = 5
        items: List[ClinicalContextItem] = []
        last_err = None
        elapsed = 0.0

        for attempt in range(1, max_retries + 1):
            try:
                start_t = time.time()
                items = ccee_engine.extract_context(text, source)
                elapsed = time.time() - start_t
                last_err = None
                break
            except Exception as e:
                last_err = e
                err_str = str(e)
                if ("503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str) and attempt < max_retries:
                    backoff = attempt * 4.0
                    print(f"  [Attempt {attempt}/{max_retries} 503/429 spike, retrying in {backoff}s...]")
                    time.sleep(backoff)
                else:
                    break

        if last_err is not None:
            err = str(last_err)
            print(f"  ✗ ERROR: {err}")
            if "429" in err or "RESOURCE_EXHAUSTED" in err or "503" in err or "UNAVAILABLE" in err:
                status = "RATE_LIMITED_OR_UNAVAILABLE"
            else:
                status = "ERROR"
            results.append({
                "id": case_id,
                "name": name,
                "status": status,
                "error": err,
            })
            continue

        items_dict = [item.to_dict() for item in items]
        print(f"  Extracted ({len(items)} items in {elapsed:.2f}s): {json.dumps(items_dict, indent=2)}")

        # Assertions / Checks
        if case.get("expect_empty"):
            if len(items) == 0:
                status = "PASS"
                print(f"  ✓ PASS: Correctly returned empty list [] for irrelevant/non-clinical input.")
            else:
                status = "FAIL"
                print(f"  ✗ FAIL: Expected empty list [], got {len(items)} items.")
        else:
            if len(items) == 0:
                status = "FAIL"
                print(f"  ✗ FAIL: Expected clinical items, got empty list.")
            else:
                # Check prohibited diagnosis words if applicable
                prohibited_raw = case.get("prohibited_words", [])
                prohibited: List[str] = prohibited_raw if isinstance(prohibited_raw, list) else []
                found_prohibited = []
                for item in items:
                    summary_lower = item.summary.lower()
                    for pw in prohibited:
                        if isinstance(pw, str) and pw in summary_lower:
                            found_prohibited.append(pw)

                if found_prohibited:
                    status = "FAIL"
                    print(f"  ✗ FAIL: Prohibited diagnostic term inferred: {found_prohibited}")
                else:
                    status = "PASS"
                    print(f"  ✓ PASS: Valid clinical extraction conforming to constraints.")

        results.append({
            "id": case_id,
            "name": name,
            "status": status,
            "items": items_dict,
        })

    print("\n" + "=" * 60)
    print("LIVE EVALUATION SUMMARY:")
    print("=" * 60)
    for r in results:
        status_symbol = "✓" if r["status"] == "PASS" else "✗"
        print(f"{status_symbol} Case {r['id']} ({r['name']}): {r['status']}")

    return results


if __name__ == "__main__":
    run_local_contract_tests()
    run_live_gemini_tests()
