"""
Final 200 Dataset Audit & Verification Script
============================================
Performs:
1. Coverage Audit (Domain, Difficulty, Provenance channel coverage, fact counts, conflict counts)
2. Duplicate Audit (Consultations, context items, clinician notes)
3. Structural Conflict Audit (All 25 conflict scenarios)
4. SHA-256 Checksum Calculation
"""

import json
import hashlib
from pathlib import Path
from collections import Counter

def audit_dataset():
    path = Path("docs/evaluation/datasets/pcif_final_200.jsonl")
    scenarios = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                scenarios.append(json.loads(line))

    total_scenarios = len(scenarios)
    domain_counts = Counter(s["domain"] for s in scenarios)
    diff_counts = Counter(s["difficulty"] for s in scenarios)

    patient_only = 0
    clinician_only = 0
    both_prov = 0
    neither_prov = 0

    longitudinal_count = 0
    distractor_count = 0
    conflict_scenarios_count = 0
    sparse_count = 0
    no_history_count = 0

    total_q_facts = 0
    total_f_facts = 0
    relevant_f_facts = 0
    irrelevant_f_facts = 0
    clinician_f_count = 0
    patient_f_count = 0
    total_conflict_groups = 0

    consultation_texts = []
    patient_summaries = []
    clinician_texts = []

    conflict_audit_results = []

    for s in scenarios:
        sid = s["scenario_id"]
        q_facts = s["current_consultation"].get("fact_units", [])
        p_curr = s.get("patient_reported_current_context", [])
        p_long = s.get("patient_reported_longitudinal_history", [])
        c_hist = s.get("clinician_authored_history", [])
        gold = s.get("gold_evidence", {})

        total_q_facts += len(q_facts)
        
        all_patient = p_curr + p_long
        has_patient = len(all_patient) > 0
        has_clinician = len(c_hist) > 0

        if has_patient and not has_clinician:
            patient_only += 1
        elif has_clinician and not has_patient:
            clinician_only += 1
        elif has_patient and has_clinician:
            both_prov += 1
        else:
            neither_prov += 1

        if len(p_long) > 0:
            longitudinal_count += 1

        if len(gold.get("irrelevant_fact_ids", [])) > 0:
            distractor_count += 1

        c_groups = gold.get("conflict_groups", [])
        if len(c_groups) > 0:
            conflict_scenarios_count += 1
            total_conflict_groups += len(c_groups)

        if s["domain"] == "sparse_history":
            sparse_count += 1
        elif s["domain"] == "no_history":
            no_history_count += 1

        total_f_facts += (len(all_patient) + len(c_hist))
        patient_f_count += len(all_patient)
        clinician_f_count += len(c_hist)

        relevant_f_facts += len(gold.get("relevant_fact_ids", []))
        irrelevant_f_facts += len(gold.get("irrelevant_fact_ids", []))

        # Duplicates tracking
        consultation_texts.append(s["current_consultation"]["text"].strip())
        for p in all_patient:
            patient_summaries.append(p["summary"].strip())
        for c in c_hist:
            clinician_texts.append(c["note"].strip())

        # Conflict audit
        if s["domain"] == "conflicting_information":
            for cg in c_groups:
                c_id = cg["conflict_id"]
                f_ids = cg["fact_ids"]
                beh = cg.get("expected_behavior")
                desc = cg.get("description", "")
                conflict_audit_results.append({
                    "scenario_id": sid,
                    "conflict_id": c_id,
                    "fact_ids": f_ids,
                    "behavior": beh,
                    "desc": desc,
                    "facts_count": len(f_ids)
                })

    # Duplicates check
    consult_dup_count = len(consultation_texts) - len(set(consultation_texts))
    patient_dup_count = len(patient_summaries) - len(set(patient_summaries))
    clinician_dup_count = len(clinician_texts) - len(set(clinician_texts))

    # SHA-256
    with open(path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()

    print("==================================================")
    print("FINAL 200 DATASET AUDIT REPORT")
    print("==================================================")
    print(f"Total Scenarios: {total_scenarios}")
    print(f"Dataset SHA-256: {sha256}")
    print("\n--- DOMAIN DISTRIBUTION ---")
    for d, c in sorted(domain_counts.items()):
        print(f"  {d}: {c}")
    print("\n--- DIFFICULTY DISTRIBUTION ---")
    for diff, c in sorted(diff_counts.items()):
        print(f"  {diff}: {c}")
    print("\n--- PROVENANCE COVERAGE (SCENARIO-LEVEL) ---")
    print(f"  Patient-reported only: {patient_only} ({patient_only/total_scenarios*100:.1f}%)")
    print(f"  Clinician-authored only: {clinician_only} ({clinician_only/total_scenarios*100:.1f}%)")
    print(f"  Both (Patient + Clinician): {both_prov} ({both_prov/total_scenarios*100:.1f}%)")
    print(f"  Neither (No-History controls): {neither_prov} ({neither_prov/total_scenarios*100:.1f}%)")
    print("\n--- STRUCTURAL COVERAGE ---")
    print(f"  Scenarios with longitudinal history: {longitudinal_count}")
    print(f"  Scenarios with distractors (irrelevant facts): {distractor_count}")
    print(f"  Scenarios with conflicts: {conflict_scenarios_count}")
    print(f"  Total conflict groups: {total_conflict_groups}")
    print(f"  Sparse-history scenarios: {sparse_count}")
    print(f"  No-history scenarios: {no_history_count}")
    print("\n--- FACT UNIT TOTALS ---")
    print(f"  Total Consultation Q facts: {total_q_facts}")
    print(f"  Total Historical F facts: {total_f_facts}")
    print(f"    - Patient-reported F facts: {patient_f_count}")
    print(f"    - Clinician-authored F facts: {clinician_f_count}")
    print(f"  Relevant F facts: {relevant_f_facts}")
    print(f"  Irrelevant F facts (distractors): {irrelevant_f_facts}")
    print("\n--- DUPLICATE AUDIT ---")
    print(f"  Duplicate Consultation texts: {consult_dup_count}")
    print(f"  Duplicate Patient context summaries: {patient_dup_count}")
    print(f"  Duplicate Clinician notes: {clinician_dup_count}")
    print("\n--- CONFLICTING INFORMATION STRUCTURAL AUDIT (25 Scenarios) ---")
    print(f"  Total Conflicting Information Scenarios checked: {len(conflict_audit_results)}")
    all_valid_conflicts = all(c['behavior'] == 'surface_for_verification' and c['facts_count'] >= 2 for c in conflict_audit_results)
    print(f"  All 25 conflict scenarios have valid behavior & >= 2 facts: {all_valid_conflicts}")

if __name__ == "__main__":
    audit_dataset()
