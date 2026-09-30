#!/usr/bin/env python3
"""
PCIF Evaluation Dataset Validator
=================================
Validates synthetic evaluation scenarios against the PCIF dataset schema and integrity rules.

Rules enforced:
1. Scenario Structure:
   - Required fields: scenario_id, split, domain, difficulty, current_consultation,
     patient_reported_current_context, patient_reported_longitudinal_history,
     clinician_authored_history, gold_evidence.
   - Split must be 'pilot' or 'final'.
   - Difficulty must be 'easy', 'medium', or 'hard'.
   - Domain must be one of the 9 allowed PCIF evaluation domains.
   - Current consultation must have non-empty 'text' (Source A - transient).
   - Optional 'fact_units' inside current_consultation use Q namespace (Q1, Q2...).

2. Fact ID Integrity:
   - Historical fact IDs (F1, F2...) must be unique within their namespace across:
     patient_reported_current_context, patient_reported_longitudinal_history, clinician_authored_history.
   - Consultation fact IDs (Q1, Q2...) must be unique within their namespace in current_consultation.fact_units.
   - relevant_fact_ids and irrelevant_fact_ids must reference historical 'F' facts only (not 'Q' consultation facts).
   - relevant_fact_ids and irrelevant_fact_ids sets must be disjoint (no overlap).
   - Conflict groups must reference valid declared fact IDs (Q and/or F, minimum 2 facts per conflict) with
     expected_behavior == 'surface_for_verification'.
   - expected_provenance keys must match declared facts and map correctly to:
     * 'current_consultation' for Q facts
     * 'patient_reported' for patient context items
     * 'clinician_authored' for clinician note items

3. Provenance & CCEE Taxonomy:
   - Patient context items must use record_type='patient_reported', valid source ('nutrition' or 'mental_wellness'),
     and one of the 11 frozen CCEE categories.
   - Clinician notes must use record_type='doctor_confirmed'.

4. Methodological Clarifications:
   - Conflict Temporal Alignment: A conflict_group may only represent facts that refer to the same or materially
     overlapping time period, OR explicitly contradict each other. Observations from clearly different periods
     must be treated as longitudinal change, not conflict. (Validator enforces structural integrity and fact IDs).
   - Relevance Does Not Mean Causation: A fact labeled 'relevant' means it is useful contextual evidence for the
     current consultation. It does NOT mean the fact caused the complaint, is a diagnosis, or medically explains
     the symptom. This distinction must be preserved during unsupported-inference scoring.
   - Evaluator Rationale: Optional 'notes_for_evaluator' records concise rationale for ambiguous relevant/irrelevant
     labels. These rationales are evaluation metadata only and are never passed to baseline or PCIF prompts.

5. Safeguards & Privacy:
   - Scenarios must not contain forbidden PII / clinical identifier patterns (SSN, MRN, real names/emails/phones).
   - No diagnostic, clinical order, or prescription ground truth labels.
"""

import sys
import json
import re
import argparse
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Frozen enumerations
ALLOWED_SPLITS: Set[str] = {"pilot", "final"}
ALLOWED_DIFFICULTIES: Set[str] = {"easy", "medium", "hard"}
ALLOWED_DOMAINS: Set[str] = {
    "nutrition",
    "mental_wellness",
    "mixed_context",
    "longitudinal_change",
    "conflicting_information",
    "irrelevant_history",
    "sparse_history",
    "no_history",
    "provenance_sensitive",
}
ALLOWED_CCEE_CATEGORIES: Set[str] = {
    "nutrition",
    "sleep",
    "stress",
    "mood",
    "hydration",
    "appetite",
    "activity",
    "symptom",
    "habit",
    "lifestyle_change",
    "other_clinically_relevant_context",
}
ALLOWED_SOURCES: Set[str] = {"nutrition", "mental_wellness"}
ALLOWED_PROVENANCE: Set[str] = {"current_consultation", "patient_reported", "clinician_authored"}
ALLOWED_CONFLICT_BEHAVIORS: Set[str] = {"surface_for_verification"}

# Forbidden PII / real-patient key markers
FORBIDDEN_KEYS: Set[str] = {
    "ssn", "social_security", "mrn", "medical_record_number",
    "patient_name", "full_name", "first_name", "last_name",
    "dob", "date_of_birth", "phone", "phone_number", "email",
    "address", "zip_code", "postal_code", "insurance_id"
}

# Forbidden diagnostic label keys (evaluation evaluates context retrieval, not diagnostic ground truth)
FORBIDDEN_DIAGNOSTIC_KEYS: Set[str] = {
    "gold_diagnosis", "gold_disease", "expected_diagnosis",
    "icd10", "icd_code", "prescribed_medication", "gold_treatment",
    "risk_probability", "diagnostic_accuracy"
}

# PII regex patterns for value scanning
PII_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "SSN pattern detected"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "Email address pattern detected"),
    (re.compile(r"\b\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), "Phone number pattern detected"),
    (re.compile(r"\bMRN[:\s]*\d{5,}\b", re.IGNORECASE), "MRN identifier pattern detected"),
]

Q_FACT_PATTERN = re.compile(r"^Q\d+$")
F_FACT_PATTERN = re.compile(r"^F\d+$")


class ValidationError(Exception):
    """Raised when a scenario fails validation rules."""
    pass


class ScenarioValidator:
    """Validates PCIF evaluation dataset scenarios."""

    def __init__(self, strict_provenance_coverage: bool = True):
        self.strict_provenance_coverage = strict_provenance_coverage

    def validate_scenario(self, scenario: Dict[str, Any], index: int = 0) -> List[str]:
        """
        Validates a single scenario dictionary.
        Returns a list of error strings. Empty list indicates success.
        """
        errors: List[str] = []
        prefix = f"Scenario[{index}]"

        if not isinstance(scenario, dict):
            return [f"{prefix}: Scenario must be a JSON object (dict)."]

        scenario_id = scenario.get("scenario_id", f"UNKNOWN_INDEX_{index}")
        prefix = f"Scenario '{scenario_id}'"

        # 1. Required top-level keys
        required_keys = [
            "scenario_id", "split", "domain", "difficulty",
            "current_consultation", "patient_reported_current_context",
            "patient_reported_longitudinal_history", "clinician_authored_history",
            "gold_evidence"
        ]
        for key in required_keys:
            if key not in scenario:
                errors.append(f"{prefix}: Missing required field '{key}'.")

        # 2. Check forbidden keys (PII & Diagnostic ground truth labels)
        self._check_forbidden_keys(scenario, prefix, errors)

        # 3. scenario_id format
        if "scenario_id" in scenario:
            if not isinstance(scenario["scenario_id"], str) or not scenario["scenario_id"].strip():
                errors.append(f"{prefix}: 'scenario_id' must be a non-empty string.")

        # 4. split
        split = scenario.get("split")
        if split not in ALLOWED_SPLITS:
            errors.append(f"{prefix}: Invalid split '{split}'. Must be one of {sorted(ALLOWED_SPLITS)}.")

        # 5. domain
        domain = scenario.get("domain")
        if domain not in ALLOWED_DOMAINS:
            errors.append(f"{prefix}: Invalid domain '{domain}'. Must be one of {sorted(ALLOWED_DOMAINS)}.")

        # 6. difficulty
        difficulty = scenario.get("difficulty")
        if difficulty not in ALLOWED_DIFFICULTIES:
            errors.append(f"{prefix}: Invalid difficulty '{difficulty}'. Must be one of {sorted(ALLOWED_DIFFICULTIES)}.")

        # 7. current_consultation and Q fact units
        all_declared_facts: Dict[str, str] = {}  # fact_id -> actual_provenance
        historical_facts: Dict[str, str] = {}      # fact_id -> actual_provenance (F facts only)

        consultation = scenario.get("current_consultation")
        if not isinstance(consultation, dict):
            errors.append(f"{prefix}: 'current_consultation' must be an object.")
        else:
            text = consultation.get("text")
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{prefix}: 'current_consultation.text' must be a non-empty string.")

            # Check optional fact_units (Q1, Q2...)
            fact_units = consultation.get("fact_units")
            if fact_units is not None:
                if not isinstance(fact_units, list):
                    errors.append(f"{prefix}: 'current_consultation.fact_units' must be a list.")
                else:
                    for q_idx, q_unit in enumerate(fact_units):
                        q_path = f"{prefix}.current_consultation.fact_units[{q_idx}]"
                        if not isinstance(q_unit, dict):
                            errors.append(f"{q_path}: Fact unit must be an object.")
                            continue
                        qid = q_unit.get("fact_id")
                        if not isinstance(qid, str) or not Q_FACT_PATTERN.match(qid):
                            errors.append(f"{q_path}: Consultation fact_id '{qid}' must follow 'Q<number>' format (e.g. Q1, Q2).")
                        elif qid in all_declared_facts:
                            errors.append(f"{q_path}: Duplicate consultation fact_id '{qid}'.")
                        else:
                            all_declared_facts[qid] = "current_consultation"

                        q_text = q_unit.get("text")
                        if not isinstance(q_text, str) or not q_text.strip():
                            errors.append(f"{q_path}: Fact unit 'text' must be a non-empty string.")

        # 8. Fact extraction and verification across historical evidence arrays (F facts)
        # 8a. patient_reported_current_context
        current_ctx = scenario.get("patient_reported_current_context")
        if not isinstance(current_ctx, list):
            errors.append(f"{prefix}: 'patient_reported_current_context' must be a list.")
        else:
            for idx, item in enumerate(current_ctx):
                self._validate_patient_context_item(
                    item, f"{prefix}.patient_reported_current_context[{idx}]",
                    all_declared_facts, historical_facts, errors
                )

        # 8b. patient_reported_longitudinal_history
        long_ctx = scenario.get("patient_reported_longitudinal_history")
        if not isinstance(long_ctx, list):
            errors.append(f"{prefix}: 'patient_reported_longitudinal_history' must be a list.")
        else:
            for idx, item in enumerate(long_ctx):
                self._validate_patient_context_item(
                    item, f"{prefix}.patient_reported_longitudinal_history[{idx}]",
                    all_declared_facts, historical_facts, errors
                )

        # 8c. clinician_authored_history
        clin_notes = scenario.get("clinician_authored_history")
        if not isinstance(clin_notes, list):
            errors.append(f"{prefix}: 'clinician_authored_history' must be a list.")
        else:
            for idx, item in enumerate(clin_notes):
                self._validate_clinician_note_item(
                    item, f"{prefix}.clinician_authored_history[{idx}]",
                    all_declared_facts, historical_facts, errors
                )

        # 9. gold_evidence validation
        gold = scenario.get("gold_evidence")
        if not isinstance(gold, dict):
            errors.append(f"{prefix}: 'gold_evidence' must be an object.")
        else:
            self._validate_gold_evidence(gold, prefix, all_declared_facts, historical_facts, errors)

        # 10. Deep PII text scanning
        self._scan_pii_strings(scenario, prefix, errors)

        return errors

    def _check_forbidden_keys(self, obj: Any, path: str, errors: List[str]) -> None:
        """Recursively checks for forbidden PII and diagnostic ground truth keys."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                lower_k = str(k).lower()
                if lower_k in FORBIDDEN_KEYS:
                    errors.append(f"{path}: Forbidden PII field detected '{k}'.")
                if lower_k in FORBIDDEN_DIAGNOSTIC_KEYS:
                    errors.append(f"{path}: Forbidden diagnostic/medication label detected '{k}'. PCIF does not evaluate diagnostic truth.")
                self._check_forbidden_keys(v, f"{path}.{k}", errors)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                self._check_forbidden_keys(item, f"{path}[{idx}]", errors)

    def _validate_patient_context_item(
        self, item: Any, item_path: str,
        all_declared_facts: Dict[str, str], historical_facts: Dict[str, str],
        errors: List[str]
    ) -> None:
        """Validates a patient-reported context item against CCEE rules + fact_id."""
        if not isinstance(item, dict):
            errors.append(f"{item_path}: Context item must be an object.")
            return

        fact_id = item.get("fact_id")
        if not isinstance(fact_id, str) or not F_FACT_PATTERN.match(fact_id):
            errors.append(f"{item_path}: Historical fact_id '{fact_id}' must follow 'F<number>' format (e.g. F1, F2).")
        else:
            if fact_id in historical_facts:
                errors.append(f"{item_path}: Duplicate historical fact_id '{fact_id}' already defined in this scenario.")
            all_declared_facts[fact_id] = "patient_reported"
            historical_facts[fact_id] = "patient_reported"

        category = item.get("category")
        if category not in ALLOWED_CCEE_CATEGORIES:
            errors.append(f"{item_path}: Invalid CCEE category '{category}'. Must be one of {sorted(ALLOWED_CCEE_CATEGORIES)}.")

        summary = item.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            errors.append(f"{item_path}: 'summary' must be a non-empty string.")

        source = item.get("source")
        if source not in ALLOWED_SOURCES:
            errors.append(f"{item_path}: Invalid source '{source}'. Must be one of {sorted(ALLOWED_SOURCES)}.")

        record_type = item.get("record_type")
        if record_type != "patient_reported":
            errors.append(f"{item_path}: 'record_type' must strictly be 'patient_reported' (got '{record_type}').")

        # Check status if present (for longitudinal items)
        if "status" in item:
            status = item.get("status")
            if status not in {"historical", "current", "superseded"}:
                errors.append(f"{item_path}: Invalid status '{status}'. Must be 'historical', 'current', or 'superseded'.")

    def _validate_clinician_note_item(
        self, item: Any, item_path: str,
        all_declared_facts: Dict[str, str], historical_facts: Dict[str, str],
        errors: List[str]
    ) -> None:
        """Validates a clinician-authored note item."""
        if not isinstance(item, dict):
            errors.append(f"{item_path}: Clinician note item must be an object.")
            return

        fact_id = item.get("fact_id")
        if not isinstance(fact_id, str) or not F_FACT_PATTERN.match(fact_id):
            errors.append(f"{item_path}: Historical fact_id '{fact_id}' must follow 'F<number>' format (e.g. F1, F2).")
        else:
            if fact_id in historical_facts:
                errors.append(f"{item_path}: Duplicate historical fact_id '{fact_id}' already defined in this scenario.")
            all_declared_facts[fact_id] = "clinician_authored"
            historical_facts[fact_id] = "clinician_authored"

        note = item.get("note")
        if not isinstance(note, str) or not note.strip():
            errors.append(f"{item_path}: 'note' must be a non-empty string.")

        record_type = item.get("record_type")
        if record_type != "doctor_confirmed":
            errors.append(f"{item_path}: 'record_type' must strictly be 'doctor_confirmed' (got '{record_type}').")

    def _validate_gold_evidence(
        self, gold: Dict[str, Any], prefix: str,
        all_declared_facts: Dict[str, str], historical_facts: Dict[str, str],
        errors: List[str]
    ) -> None:
        """Validates gold_evidence fields, cross-referencing declared fact_ids."""
        # 1. relevant_fact_ids (must be historical F facts only)
        rel_ids = gold.get("relevant_fact_ids")
        if not isinstance(rel_ids, list):
            errors.append(f"{prefix}.gold_evidence: 'relevant_fact_ids' must be a list.")
            rel_set = set()
        else:
            rel_set = set(rel_ids)
            for fid in rel_ids:
                if fid not in historical_facts:
                    if fid.startswith("Q"):
                        errors.append(f"{prefix}.gold_evidence.relevant_fact_ids: '{fid}' is a consultation fact. relevant_fact_ids must contain historical 'F' facts only.")
                    else:
                        errors.append(f"{prefix}.gold_evidence.relevant_fact_ids: Referenced fact_id '{fid}' does not exist in declared historical facts.")

        # 2. irrelevant_fact_ids (must be historical F facts only)
        irrel_ids = gold.get("irrelevant_fact_ids")
        if not isinstance(irrel_ids, list):
            errors.append(f"{prefix}.gold_evidence: 'irrelevant_fact_ids' must be a list.")
            irrel_set = set()
        else:
            irrel_set = set(irrel_ids)
            for fid in irrel_ids:
                if fid not in historical_facts:
                    if fid.startswith("Q"):
                        errors.append(f"{prefix}.gold_evidence.irrelevant_fact_ids: '{fid}' is a consultation fact. irrelevant_fact_ids must contain historical 'F' facts only.")
                    else:
                        errors.append(f"{prefix}.gold_evidence.irrelevant_fact_ids: Referenced fact_id '{fid}' does not exist in declared historical facts.")

        # 3. Disjoint check between relevant and irrelevant
        overlap = rel_set.intersection(irrel_set)
        if overlap:
            errors.append(f"{prefix}.gold_evidence: Historical fact IDs cannot be both relevant and irrelevant: {sorted(overlap)}.")

        # 4. conflict_groups (can reference Q and/or F facts)
        conflicts = gold.get("conflict_groups")
        if not isinstance(conflicts, list):
            errors.append(f"{prefix}.gold_evidence: 'conflict_groups' must be a list.")
        else:
            seen_conflict_ids = set()
            for c_idx, c_group in enumerate(conflicts):
                c_path = f"{prefix}.gold_evidence.conflict_groups[{c_idx}]"
                if not isinstance(c_group, dict):
                    errors.append(f"{c_path}: Conflict group must be an object.")
                    continue

                cid = c_group.get("conflict_id")
                if not isinstance(cid, str) or not cid.strip():
                    errors.append(f"{c_path}: Missing or invalid 'conflict_id'.")
                else:
                    if cid in seen_conflict_ids:
                        errors.append(f"{c_path}: Duplicate conflict_id '{cid}' in conflict_groups.")
                    seen_conflict_ids.add(cid)

                fids = c_group.get("fact_ids")
                if not isinstance(fids, list) or len(fids) < 2:
                    errors.append(f"{c_path}: 'fact_ids' must be a list with at least 2 fact IDs.")
                else:
                    for fid in fids:
                        if fid not in all_declared_facts:
                            errors.append(f"{c_path}: Fact '{fid}' in conflict group does not exist in declared scenario facts.")

                behavior = c_group.get("expected_behavior")
                if behavior not in ALLOWED_CONFLICT_BEHAVIORS:
                    errors.append(f"{c_path}: Invalid expected_behavior '{behavior}'. Must be 'surface_for_verification'.")

        # 5. expected_provenance
        exp_prov = gold.get("expected_provenance")
        if not isinstance(exp_prov, dict):
            errors.append(f"{prefix}.gold_evidence: 'expected_provenance' must be an object mapping fact_id -> provenance.")
        else:
            for fid, prov in exp_prov.items():
                if fid not in all_declared_facts:
                    errors.append(f"{prefix}.gold_evidence.expected_provenance: Key '{fid}' is not a declared fact_id in this scenario.")
                elif prov not in ALLOWED_PROVENANCE:
                    errors.append(f"{prefix}.gold_evidence.expected_provenance['{fid}']: Invalid provenance '{prov}'. Must be one of {sorted(ALLOWED_PROVENANCE)}.")
                else:
                    # Check consistency with declared item provenance
                    actual_prov = all_declared_facts[fid]
                    if prov != actual_prov:
                        errors.append(f"{prefix}.gold_evidence.expected_provenance['{fid}']: Mismatch with declared item origin. Expected '{prov}' but item is '{actual_prov}'.")

            if self.strict_provenance_coverage:
                missing_prov = set(all_declared_facts.keys()) - set(exp_prov.keys())
                if missing_prov:
                    errors.append(f"{prefix}.gold_evidence.expected_provenance: Missing provenance mapping for declared facts: {sorted(missing_prov)}.")

    def _scan_pii_strings(self, obj: Any, path: str, errors: List[str]) -> None:
        """Scans string values for common PII patterns."""
        if isinstance(obj, str):
            for regex, desc in PII_PATTERNS:
                if regex.search(obj):
                    errors.append(f"{path}: Potential PII detected ({desc}).")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                self._scan_pii_strings(v, f"{path}.{k}", errors)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                self._scan_pii_strings(item, f"{path}[{idx}]", errors)


def load_dataset_file(file_path: Path) -> List[Dict[str, Any]]:
    """Loads either a .json file (single object or list) or a .jsonl file (lines of objects)."""
    scenarios: List[Dict[str, Any]] = []
    if file_path.suffix.lower() == ".jsonl":
        with open(file_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                try:
                    obj = json.loads(clean_line)
                    scenarios.append(obj)
                except Exception as e:
                    raise ValueError(f"Line {line_no} JSON parse error: {e}")
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                scenarios = data
            elif isinstance(data, dict):
                scenarios = [data]
            else:
                raise ValueError("Root JSON must be an object or a list of objects.")
    return scenarios


def validate_dataset_data(data: Any, strict: bool = True) -> Tuple[bool, List[str]]:
    """
    Validates data which can be a single scenario dict or a list of scenario dicts.
    Returns (is_valid, list_of_errors).
    """
    validator = ScenarioValidator(strict_provenance_coverage=strict)
    all_errors: List[str] = []
    seen_scenario_ids: Set[str] = set()

    if isinstance(data, dict):
        scenarios = [data]
    elif isinstance(data, list):
        scenarios = data
    else:
        return False, ["Root dataset structure must be a scenario object or a list of scenario objects."]

    for idx, scn in enumerate(scenarios):
        scn_id = scn.get("scenario_id") if isinstance(scn, dict) else None
        if scn_id:
            if scn_id in seen_scenario_ids:
                all_errors.append(f"Global dataset error: Duplicate scenario_id '{scn_id}' detected across scenarios.")
            seen_scenario_ids.add(scn_id)

        errs = validator.validate_scenario(scn, index=idx)
        all_errors.extend(errs)

    return (len(all_errors) == 0), all_errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PCIF synthetic evaluation scenario dataset files (.json, .jsonl).")
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Path to a scenario JSON/JSONL file, or directory containing scenario dataset files."
    )
    parser.add_argument(
        "--non-strict-provenance",
        action="store_true",
        help="Do not enforce that expected_provenance covers all declared scenario facts."
    )
    args = parser.parse_args()

    target_path_str = args.target
    if not target_path_str:
        default_dir = Path(__file__).parent
        print(f"No target specified. Checking directory: {default_dir}")
        target_path = default_dir
    else:
        target_path = Path(target_path_str)

    if not target_path.exists():
        print(f"Error: Target path '{target_path}' does not exist.", file=sys.stderr)
        return 1

    files_to_check: List[Path] = []
    if target_path.is_file():
        if target_path.suffix.lower() in {".json", ".jsonl"} and target_path.name != "pcif_dataset_schema.json":
            files_to_check.append(target_path)
        else:
            print(f"Skipping non-dataset or schema file: {target_path}")
            return 0
    elif target_path.is_dir():
        for ext in ("*.json", "*.jsonl"):
            for p in sorted(target_path.glob(f"**/{ext}")):
                if p.name != "pcif_dataset_schema.json":
                    files_to_check.append(p)

    if not files_to_check:
        print(f"No scenario JSON/JSONL files found to validate in '{target_path}'.")
        print("Dataset validator is active and ready.")
        return 0

    total_scenarios = 0
    total_errors = 0
    strict = not args.non_strict_provenance

    print(f"Validating {len(files_to_check)} file(s)...")
    for file_p in files_to_check:
        try:
            scenarios = load_dataset_file(file_p)
        except Exception as e:
            print(f"[{file_p.name}] Load Error: {e}")
            total_errors += 1
            continue

        is_valid, errors = validate_dataset_data(scenarios, strict=strict)
        count = len(scenarios)
        total_scenarios += count

        if is_valid:
            print(f"  [PASS] {file_p.name} ({count} scenario(s))")
        else:
            print(f"  [FAIL] {file_p.name} ({count} scenario(s)) - {len(errors)} error(s):")
            for err in errors:
                print(f"    - {err}")
            total_errors += len(errors)

    print("\n" + "=" * 50)
    print(f"Summary: {total_scenarios} scenario(s) checked across {len(files_to_check)} file(s).")
    if total_errors == 0:
        print("Result: ALL SCENARIOS PASSED VALIDATION.")
        return 0
    else:
        print(f"Result: VALIDATION FAILED with {total_errors} total error(s).")
        return 1


if __name__ == "__main__":
    sys.exit(main())
