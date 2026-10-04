"""
PCIF Final Evaluation Runner
============================
Executes paired evaluation of 200 Final Scenarios under:
- Condition A: BASELINE (current consultation only, empty prior history)
- Condition B: PCIF (current consultation + patient context + clinician notes)

Strict Protocol Enforcements:
1. Production isolation: Read-only offline evaluation. No DB writes or endpoint modifications.
2. Controlled variables: Identical Gemini model, temperature=0.0, Doctor Context system instruction, output schema.
3. Information hiding: Gold evidence (relevant/irrelevant IDs, conflicts, evaluator notes, Q/F IDs) is NEVER sent to Gemini.
4. Output persistence: Raw responses saved incrementally to disk before scoring.
5. Transient failure handling: Frozen retry/backoff policy (MAX_RETRIES=3, backoff 2s, 4s).
6. State preservation: Resumes from existing completed successful calls if interrupted.
"""

import os
import sys
import json
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.app.core.config import settings
from backend.app.services.llm_service import llm_service, DoctorContextResponseSchema
from backend.app.prompts import DOCTOR_CONTEXT_SYSTEM_INSTRUCTION
from google.genai import types

MAX_RETRIES = 3
INITIAL_BACKOFF = 2.0


def clean_patient_context_items(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned = []
    for item in raw_items:
        clean_item = {
            "category": item.get("category"),
            "summary": item.get("summary"),
            "source": item.get("source"),
            "record_type": item.get("record_type", "patient_reported"),
            "value": item.get("value"),
            "duration": item.get("duration"),
        }
        cleaned.append(clean_item)
    return cleaned


def clean_clinician_notes_items(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned = []
    for item in raw_items:
        clean_item = {
            "note": item.get("note", ""),
            "provenance": "clinician_authored",
            "saved_at": item.get("timestamp") or item.get("saved_at"),
        }
        cleaned.append(clean_item)
    return cleaned


def build_evaluation_prompt(
    scenario_id: str,
    consultation_text: str,
    condition: str,
    scenario: Dict[str, Any]
) -> str:
    if condition == "baseline":
        clean_current = []
        clean_history = []
        clean_clinician_notes = []
    elif condition == "pcif":
        clean_current = clean_patient_context_items(scenario.get("patient_reported_current_context", []))
        clean_history = clean_patient_context_items(scenario.get("patient_reported_longitudinal_history", []))
        clean_clinician_notes = clean_clinician_notes_items(scenario.get("clinician_authored_history", []))
    else:
        raise ValueError(f"Unknown condition '{condition}'")

    prompt = (
        f"PATIENT ID: {scenario_id}\n\n"
        f"[SOURCE A: CURRENT CLINICIAN CONSULTATION NOTES]\n\"\"\"\n{consultation_text.strip()}\n\"\"\"\n\n"
        f"[SOURCE B: PATIENT-REPORTED CONTEXT]\n"
        f"Active Current Patient-Reported Profile:\n{json.dumps(clean_current, indent=2)}\n\n"
        f"Longitudinal Patient-Reported History:\n{json.dumps(clean_history, indent=2)}\n\n"
        f"[SOURCE C: CLINICIAN-AUTHORED HISTORICAL NOTES]\n"
        f"Clinician-Authored Notes History:\n{json.dumps(clean_clinician_notes, indent=2)}\n\n"
        "Analyze the above three sources according to your system instructions. "
        "Synthesize relevant background context with the consultation notes and return a structured DoctorContextResponse JSON."
    )
    return prompt


def execute_model_call(
    prompt: str,
    model_name: str,
    system_instruction: str,
    client: Any
) -> Tuple[Dict[str, Any], int]:
    """
    Executes a single model call with controlled parameters and frozen retry policy.
    Returns (assistant_response, retries_taken).
    """
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=DoctorContextResponseSchema,
        temperature=0.0,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    last_err = None
    retries_taken = 0
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            raw_text = response.text or "{}"
            data = json.loads(raw_text)
            
            return {
                "context_summary": data.get("context_summary", ""),
                "relevant_current_context": data.get("relevant_current_context", []),
                "relevant_longitudinal_changes": data.get("relevant_longitudinal_changes", []),
                "relevant_clinician_notes": data.get("relevant_clinician_notes", []),
                "items_to_verify": data.get("items_to_verify", [])
            }, retries_taken
        except Exception as e:
            last_err = e
            if attempt < MAX_RETRIES:
                retries_taken += 1
                sleep_sec = INITIAL_BACKOFF * (2 ** (attempt - 1))
                time.sleep(sleep_sec)

    raise RuntimeError(f"Model call failed after {MAX_RETRIES} attempts: {last_err}") from last_err


def run_final_evaluation(
    dataset_path: str = "docs/evaluation/datasets/pcif_final_200.jsonl",
    raw_output_path: str = "docs/evaluation/results/final_raw_outputs.jsonl"
) -> Dict[str, Any]:
    client = llm_service._get_client()
    if client is None:
        raise RuntimeError("Gemini client unavailable. GEMINI_API_KEY must be configured in backend/.env.")

    model_name = os.getenv("GEMINI_MODEL", settings.GEMINI_MODEL) or "gemini-3.1-flash-lite"
    model_config_id = f"{model_name}@temperature=0.0"
    prompt_hash = hashlib.sha256(DOCTOR_CONTEXT_SYSTEM_INSTRUCTION.encode("utf-8")).hexdigest()[:12]

    # Load dataset
    scenarios = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                scenarios.append(json.loads(line))

    raw_output_file = Path(raw_output_path)
    raw_output_file.parent.mkdir(parents=True, exist_ok=True)

    # Load existing completed calls to preserve progress
    existing_records: Dict[Tuple[str, str], Dict[str, Any]] = {}
    if raw_output_file.exists():
        with open(raw_output_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        rec = json.loads(line)
                        if rec.get("run_status") == "success":
                            existing_records[(rec["scenario_id"], rec["condition"])] = rec
                    except Exception:
                        pass

    # Open file for appending or rewriting
    # To be strictly atomic and clean, rewrite existing successful records and append incrementally
    completed_calls = len(existing_records)
    total_transient_retries = 0
    total_permanent_failures = 0

    with open(raw_output_file, "w", encoding="utf-8") as f:
        for rec in existing_records.values():
            f.write(json.dumps(rec) + "\n")
        f.flush()

    for idx, sc in enumerate(scenarios, start=1):
        sc_id = sc["scenario_id"]
        domain = sc["domain"]
        difficulty = sc["difficulty"]
        c_text = sc["current_consultation"]["text"]

        cond_statuses = {}

        for condition in ["baseline", "pcif"]:
            key = (sc_id, condition)
            if key in existing_records:
                cond_statuses[condition] = "SUCCESS (cached)"
                continue

            timestamp = datetime.now(timezone.utc).isoformat()
            prompt = build_evaluation_prompt(sc_id, c_text, condition, sc)

            try:
                assistant_resp, retries = execute_model_call(
                    prompt=prompt,
                    model_name=model_name,
                    system_instruction=DOCTOR_CONTEXT_SYSTEM_INSTRUCTION,
                    client=client
                )
                total_transient_retries += retries
                run_record = {
                    "scenario_id": sc_id,
                    "domain": domain,
                    "difficulty": difficulty,
                    "condition": condition,
                    "model_configuration_identifier": model_config_id,
                    "prompt_hash": prompt_hash,
                    "run_timestamp": timestamp,
                    "assistant_response": assistant_resp,
                    "run_status": "success"
                }
                completed_calls += 1
                cond_statuses[condition] = "SUCCESS" if retries == 0 else "RETRY"
            except Exception as e:
                total_permanent_failures += 1
                run_record = {
                    "scenario_id": sc_id,
                    "domain": domain,
                    "difficulty": difficulty,
                    "condition": condition,
                    "model_configuration_identifier": model_config_id,
                    "prompt_hash": prompt_hash,
                    "run_timestamp": timestamp,
                    "error_message": str(e),
                    "run_status": "failed"
                }
                cond_statuses[condition] = "FAILURE"

            # Incrementally write and flush to disk
            with open(raw_output_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(run_record) + "\n")
                f.flush()

            # Brief rate-limit pause
            time.sleep(0.1)

        # Progress display after each paired scenario as requested
        print(f"Scenario {idx}/200")
        print(f"Baseline: {cond_statuses.get('baseline', 'SKIPPED')}")
        print(f"PCIF: {cond_statuses.get('pcif', 'SKIPPED')}")
        print(f"Completed calls: {completed_calls}/400")
        print(f"Transient retries: {total_transient_retries}")
        print(f"Permanent failures: {total_permanent_failures}")
        print("-" * 30, flush=True)

    return {
        "dataset_path": dataset_path,
        "scenario_count": len(scenarios),
        "completed_calls": completed_calls,
        "transient_retries": total_transient_retries,
        "permanent_failures": total_permanent_failures,
        "raw_output_path": str(raw_output_file)
    }

if __name__ == "__main__":
    from typing import Tuple
    run_final_evaluation()
