"""
PCIF Pilot Evaluation Runner
============================
Executes paired evaluation of 50 Pilot Scenarios under:
- Condition A: BASELINE (current consultation only, empty prior history)
- Condition B: PCIF (current consultation + patient context + clinician notes)

Strict Protocol Enforcements:
1. Production isolation: Read-only offline evaluation. No DB writes or endpoint modifications.
2. Controlled variables: Identical Gemini model, temperature=0.0, Doctor Context system instruction, output schema.
3. Information hiding: Gold evidence (relevant/irrelevant IDs, conflicts, evaluator notes, Q/F IDs) is NEVER sent to Gemini.
4. Output persistence: Raw responses saved to docs/evaluation/results/pilot_raw_outputs.jsonl before scoring.
5. Transient failure handling: Documented retries with backoff; failed calls recorded and excluded from zero-scoring.
"""

import os
import sys
import json
import time
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Add workspace root to sys.path
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
    """
    Cleans evaluation metadata from patient context items before prompt construction.
    Strips fact_id, status, observed_period, etc.
    """
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
    """
    Cleans evaluation metadata from clinician note items before prompt construction.
    Strips fact_id, etc.
    """
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
    """
    Constructs the exact internal Doctor Context prompt for Baseline vs PCIF condition.
    """
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
) -> Dict[str, Any]:
    """
    Executes a single model call with controlled parameters and retry policy.
    """
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=DoctorContextResponseSchema,
        temperature=0.0,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            raw_text = response.text or "{}"
            data = json.loads(raw_text)
            
            # Format into clean standard schema response
            return {
                "context_summary": data.get("context_summary", ""),
                "relevant_current_context": data.get("relevant_current_context", []),
                "relevant_longitudinal_changes": data.get("relevant_longitudinal_changes", []),
                "relevant_clinician_notes": data.get("relevant_clinician_notes", []),
                "items_to_verify": data.get("items_to_verify", [])
            }
        except Exception as e:
            last_err = e
            error_str = str(e)
            logger.warning(f"Model call attempt {attempt}/{MAX_RETRIES} failed: {error_str}")
            if attempt < MAX_RETRIES:
                sleep_sec = INITIAL_BACKOFF * (2 ** (attempt - 1))
                time.sleep(sleep_sec)

    raise RuntimeError(f"Model call failed after {MAX_RETRIES} attempts: {last_err}") from last_err

def run_pilot_evaluation(
    dataset_path: str = "docs/evaluation/datasets/pcif_pilot_50.jsonl",
    raw_output_path: str = "docs/evaluation/results/pilot_raw_outputs.jsonl"
) -> Dict[str, Any]:
    """
    Runs the 50 pilot scenarios across Baseline and PCIF conditions.
    Saves raw outputs to JSONL.
    """
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

    logger.info(f"Loaded {len(scenarios)} pilot scenarios from {dataset_path}")
    logger.info(f"Configured Model: {model_name} (Identifier: {model_config_id})")

    raw_output_file = Path(raw_output_path)
    raw_output_file.parent.mkdir(parents=True, exist_ok=True)

    outputs = []
    successful_calls = 0
    failed_calls = 0
    failures = []

    # Execute matched paired runs: Condition A (Baseline) and Condition B (PCIF)
    for idx, sc in enumerate(scenarios, start=1):
        sc_id = sc["scenario_id"]
        domain = sc["domain"]
        difficulty = sc["difficulty"]
        c_text = sc["current_consultation"]["text"]

        logger.info(f"[{idx}/{len(scenarios)}] Running Scenario {sc_id} ({domain}, {difficulty})...")

        for condition in ["baseline", "pcif"]:
            timestamp = datetime.now(timezone.utc).isoformat()
            prompt = build_evaluation_prompt(sc_id, c_text, condition, sc)

            try:
                assistant_resp = execute_model_call(
                    prompt=prompt,
                    model_name=model_name,
                    system_instruction=DOCTOR_CONTEXT_SYSTEM_INSTRUCTION,
                    client=client
                )
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
                successful_calls += 1
            except Exception as e:
                logger.error(f"Execution failed for {sc_id} [{condition}]: {e}")
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
                failed_calls += 1
                failures.append({
                    "scenario_id": sc_id,
                    "condition": condition,
                    "error": str(e)
                })

            outputs.append(run_record)
            # Brief rate-limit courtesy pause
            time.sleep(0.2)

    # Save raw outputs
    with open(raw_output_file, "w", encoding="utf-8") as f:
        for out in outputs:
            f.write(json.dumps(out) + "\n")

    logger.info(f"Raw outputs written to {raw_output_file} ({len(outputs)} records: {successful_calls} success, {failed_calls} failed)")

    return {
        "dataset_path": dataset_path,
        "scenario_count": len(scenarios),
        "total_calls": len(outputs),
        "successful_calls": successful_calls,
        "failed_calls": failed_calls,
        "failures": failures,
        "model_configuration_identifier": model_config_id,
        "prompt_hash": prompt_hash,
        "raw_output_path": str(raw_output_file)
    }

if __name__ == "__main__":
    rep = run_pilot_evaluation()
    print(json.dumps(rep, indent=2))
