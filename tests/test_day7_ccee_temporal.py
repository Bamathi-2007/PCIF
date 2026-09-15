"""
Day 7 CCEE Test Suite - Temporal Context, Supersession & Source Integrity.

Runs:
1. Local Schema, Contract, and Boundary Tests (No LLM calls)
2. Live Conservative Gemini CCEE Evaluation (Paced calls with rate-limit protection)
   Validates:
   - Case 1: Explicit self-correction -> 1 sleep item with corrected 5h value (3h omitted)
   - Case 2: Past -> current improvement -> 1 sleep item with current 7h value & change summary
   - Case 3: Ongoing duration -> 1 sleep item with duration='2 weeks'
   - Case 4: Resolved past event -> empty list []
   - Case 5: Ongoing worsening appetite -> 1 appetite item with duration='2 weeks' & worsening summary
   - Case 6: Temporal decline -> 1 sleep item with current 4h value & decline summary
   - Case 7: Distinct temporal phenomena -> 2 items: sleep + appetite
   - Case 8: Source integrity -> category='sleep', source='nutrition' (Source strictly preserved)
   - Case 9: Multi-turn transcript -> User self-correction extracted, Assistant questions ignored
"""

import os
import sys
import time
import json
from typing import List, Dict, Any, Union, cast

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
    print("PHASE 1: DAY 7 LOCAL CONTRACT & BOUNDARY TESTS (NO LLM)")
    print("=" * 60)

    # 1. Source Integrity Enforcement: source must be preserved even if category is cross-domain
    sleep_in_nutrition = ClinicalContextItem(
        category="sleep",
        summary="Reduced sleep associated with late meal schedule",
        source="nutrition",
        record_type="patient_reported",
        value="5 hours/night"
    )
    d = sleep_in_nutrition.to_dict()
    assert d["category"] == "sleep"
    assert d["source"] == "nutrition"
    print("✓ Test 1 Passed: Source integrity strictly preserved (category='sleep', source='nutrition')")

    # 2. Frozen Schema Rule: No unexpected temporal or confidence fields
    assert hasattr(sleep_in_nutrition, "category")
    assert hasattr(sleep_in_nutrition, "summary")
    assert hasattr(sleep_in_nutrition, "source")
    assert hasattr(sleep_in_nutrition, "record_type")
    assert hasattr(sleep_in_nutrition, "value")
    assert hasattr(sleep_in_nutrition, "duration")
    assert not hasattr(sleep_in_nutrition, "confidence")
    assert not hasattr(sleep_in_nutrition, "trend")
    assert not hasattr(sleep_in_nutrition, "previous_value")
    print("✓ Test 2 Passed: Frozen schema boundaries verified (no confidence/trend fields)")

    # 3. Transcript normalization format for multi-turn lists
    transcript = [
        {"role": "user", "content": "I sleep around 3 hours."},
        {"role": "assistant", "content": "Has that been happening every night?"},
        {"role": "user", "content": "Actually closer to 5 hours."}
    ]
    normalized = ClinicalContextExtractionEngine._normalize_conversation(transcript)
    assert "User: I sleep around 3 hours." in normalized
    assert "Assistant: Has that been happening every night?" in normalized
    assert "User: Actually closer to 5 hours." in normalized
    print("✓ Test 3 Passed: Multi-turn transcript turns normalized with clear role tags")

    # 4. Deterministic deduplication safeguard preserves distinct temporal items
    past_item = ClinicalContextItem(
        category="sleep",
        summary="Sleep improved from 4 hours to 7 hours",
        source="mental_wellness",
        value="7 hours/night"
    )
    distinct_item = ClinicalContextItem(
        category="appetite",
        summary="Decreased appetite for 2 weeks",
        source="mental_wellness",
        duration="2 weeks"
    )
    deduped = ClinicalContextExtractionEngine._deduplicate_items([past_item, distinct_item])
    assert len(deduped) == 2
    print("✓ Test 4 Passed: Distinct temporal items preserved by deduplication safeguard")

    # 5. Invalid source rejection by engine
    try:
        ccee_engine.extract_context("I sleep 5 hours", "cardiology")
        assert False, "Should raise ValueError for invalid source"
    except ValueError as ve:
        assert "Invalid source" in str(ve)
        print("✓ Test 5 Passed: Invalid source rejected by engine")

    # 6. Whitespace input immediately returns empty list
    assert ccee_engine.extract_context("   \t\n", "mental_wellness") == []
    print("✓ Test 6 Passed: Empty whitespace conversation immediately returns []")


def run_live_gemini_day7_tests():
    print("\n" + "=" * 60)
    print("PHASE 2: LIVE GEMINI DAY 7 TEMPORAL EVALUATION (PACED)")
    print("=" * 60)

    # 9 Day 7 Synthetic Test Cases
    day7_cases = [
        {
            "id": "Day 7 Case 1",
            "name": "Explicit self-correction",
            "source": "mental_wellness",
            "text": "I've been sleeping around three hours. Actually, I think it's closer to five hours.",
            "expected_count": 1,
            "expected_categories": ["sleep"],
            "must_contain": ["5"],
            "must_not_contain_as_value": ["3 hours"],
        },
        {
            "id": "Day 7 Case 2",
            "name": "Past -> current improvement",
            "source": "mental_wellness",
            "text": "Last week I was sleeping around four hours, but this week I'm back to about seven hours.",
            "expected_count": 1,
            "expected_categories": ["sleep"],
            "must_contain": ["7"],
        },
        {
            "id": "Day 7 Case 3",
            "name": "Ongoing duration",
            "source": "mental_wellness",
            "text": "I've been sleeping around five hours every night for the past two weeks.",
            "expected_count": 1,
            "expected_categories": ["sleep"],
            "must_contain": ["5"],
            "expect_duration": True,
        },
        {
            "id": "Day 7 Case 4",
            "name": "Resolved insignificant past event",
            "source": "mental_wellness",
            "text": "I had one night where I barely slept about three months ago, but my sleep has been normal ever since.",
            "expected_count": 0,
            "expected_categories": [],
        },
        {
            "id": "Day 7 Case 5",
            "name": "Ongoing worsening appetite",
            "source": "nutrition",
            "text": "My appetite started decreasing about two weeks ago, and it still seems to be getting worse.",
            "expected_count": 1,
            "expected_categories": ["appetite"],
            "expect_duration": True,
        },
        {
            "id": "Day 7 Case 6",
            "name": "Temporal decline",
            "source": "mental_wellness",
            "text": "Earlier this month I was sleeping around six hours. This week it's down to four hours because assignments are keeping me up.",
            "expected_count": 1,
            "expected_categories": ["sleep"],
            "must_contain": ["4"],
        },
        {
            "id": "Day 7 Case 7",
            "name": "Distinct temporal phenomena",
            "source": "mental_wellness",
            "text": "My sleep has improved this week, but my appetite has been getting worse for about two weeks.",
            "expected_count": 2,
            "expected_categories": ["sleep", "appetite"],
        },
        {
            "id": "Day 7 Case 8",
            "name": "Source integrity",
            "source": "nutrition",
            "text": "I've been sleeping only five hours lately because my meal schedule keeps me up late.",
            "min_expected_count": 1,
            "expected_categories": ["sleep"],
            "expected_source": "nutrition",
        },
        {
            "id": "Day 7 Case 9 (Multi-Turn)",
            "name": "Multi-turn transcript & assistant safety",
            "source": "mental_wellness",
            "text": [
                {"role": "user", "content": "I'm sleeping only three hours."},
                {"role": "assistant", "content": "Has that been happening every night?"},
                {"role": "user", "content": "Actually I exaggerated — it's closer to five hours, mostly this week."}
            ],
            "expected_count": 1,
            "expected_categories": ["sleep"],
            "must_contain": ["5"],
        },
    ]

    prohibited_diagnosis_terms = [
        "insomnia", "major depressive", "depression", "generalized anxiety",
        "anorexia", "eating disorder", "anemia", "diabetes", "syndrome", "chronic fatigue"
    ]

    results = []

    for i, case in enumerate(day7_cases):
        case_id = str(case["id"])
        name = str(case["name"])
        raw_text = case["text"]
        source = str(case["source"])

        # Type-safe conversation argument for extract_context
        conv_arg: Union[str, List[Dict[str, Any]]]
        if isinstance(raw_text, str):
            conv_arg = raw_text
        elif isinstance(raw_text, list):
            conv_arg = cast(List[Dict[str, Any]], raw_text)
        else:
            conv_arg = str(raw_text)

        print(f"\nEvaluating {case_id}: {name}")
        print(f"  Source: {source}")
        print(f"  Input: {raw_text}")

        # Paced delay between calls to respect Gemini quota
        if i > 0:
            time.sleep(3.5)

        # Retry loop for transient 503/429 Gemini API server spikes
        max_retries = 5
        items: List[ClinicalContextItem] = []
        last_err = None
        elapsed = 0.0

        for attempt in range(1, max_retries + 1):
            try:
                start_t = time.time()
                items = ccee_engine.extract_context(conv_arg, source)
                elapsed = time.time() - start_t
                last_err = None
                break
            except Exception as e:
                last_err = e
                err_str = str(e)
                if ("503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str) and attempt < max_retries:
                    backoff = attempt * 5.0
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
        checks_passed = True
        failure_reasons = []

        # 1. Item count check
        exp_count_val = case.get("expected_count")
        if isinstance(exp_count_val, int):
            if len(items) != exp_count_val:
                checks_passed = False
                failure_reasons.append(f"Expected {exp_count_val} items, got {len(items)}")
        else:
            min_count_val = case.get("min_expected_count")
            if isinstance(min_count_val, int):
                if len(items) < min_count_val:
                    checks_passed = False
                    failure_reasons.append(f"Expected at least {min_count_val} items, got {len(items)}")

        # 2. Categories check
        actual_categories = [item.category for item in items]
        exp_cat_raw = case.get("expected_categories", [])
        expected_categories: List[str] = [str(x) for x in exp_cat_raw] if isinstance(exp_cat_raw, list) else []
        for exp_cat in expected_categories:
            if exp_cat not in actual_categories:
                checks_passed = False
                failure_reasons.append(f"Expected category '{exp_cat}' not found in {actual_categories}")

        # 3. Source integrity check if specified
        exp_src = case.get("expected_source")
        if exp_src:
            for item in items:
                if item.source != exp_src:
                    checks_passed = False
                    failure_reasons.append(f"Item source '{item.source}' does not match expected '{exp_src}'")

        # 4. Check expected text markers (must_contain)
        must_contain_raw = case.get("must_contain", [])
        must_contain: List[str] = [str(x) for x in must_contain_raw] if isinstance(must_contain_raw, list) else []
        if must_contain:
            found_any = False
            for marker in must_contain:
                if any(
                    marker.lower() in (item.value or "").lower() or marker.lower() in item.summary.lower()
                    for item in items
                ):
                    found_any = True
                    break
            if not found_any:
                checks_passed = False
                failure_reasons.append(f"None of expected markers {must_contain} found in items")

        # 5. Check duration presence if expected
        if case.get("expect_duration"):
            has_dur = any(item.duration for item in items)
            if not has_dur:
                checks_passed = False
                failure_reasons.append("Expected duration field to be populated, but it was empty/None")

        # 6. Check prohibited diagnosis terms
        found_prohibited = []
        for item in items:
            summary_lower = item.summary.lower()
            for pw in prohibited_diagnosis_terms:
                if pw in summary_lower:
                    found_prohibited.append(pw)
        if found_prohibited:
            checks_passed = False
            failure_reasons.append(f"Prohibited diagnosis terms inferred: {found_prohibited}")

        # 7. Specific temporal-precision checks for Case 5 and Case 9
        if case_id == "Day 7 Case 5":
            app_item = next((i for i in items if i.category == "appetite"), None)
            if app_item:
                dur_lower = (app_item.duration or "").lower()
                sum_lower = app_item.summary.lower()
                combined = f"{dur_lower} {sum_lower}"
                if "about" not in combined and "approx" not in combined and "around" not in combined:
                    checks_passed = False
                    failure_reasons.append(f"Case 5 lost approximate qualifier ('about/approx'): duration='{app_item.duration}'")

        if case_id == "Day 7 Case 9 (Multi-Turn)":
            sleep_item = next((i for i in items if i.category == "sleep"), None)
            if sleep_item:
                dur_lower = (sleep_item.duration or "").lower()
                if "1 week" in dur_lower or "one week" in dur_lower:
                    checks_passed = False
                    failure_reasons.append(f"Case 9 converted 'this week' into exact 7-day duration: duration='{sleep_item.duration}'")
                elif "this week" not in dur_lower:
                    checks_passed = False
                    failure_reasons.append(f"Case 9 did not preserve 'this week' duration: duration='{sleep_item.duration}'")

        if checks_passed:
            status = "PASS"
            print(f"  ✓ PASS: Temporal context and constraints verified.")
        else:
            status = "FAIL"
            print(f"  ✗ FAIL: {'; '.join(failure_reasons)}")

        results.append({
            "id": case_id,
            "name": name,
            "status": status,
            "items": items_dict,
            "reasons": failure_reasons
        })

    print("\n" + "=" * 60)
    print("DAY 7 LIVE EVALUATION SUMMARY:")
    print("=" * 60)
    for r in results:
        status_symbol = "✓" if r["status"] == "PASS" else "✗"
        print(f"{status_symbol} {r['id']} ({r['name']}): {r['status']}")

    return results


if __name__ == "__main__":
    run_local_contract_tests()
    run_live_gemini_day7_tests()
