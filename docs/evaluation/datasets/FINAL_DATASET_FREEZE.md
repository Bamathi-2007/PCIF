# PCIF Final 200 Evaluation Dataset Freeze

**Freeze Date & Time:** 2026-09-30T15:40:00Z  
**Dataset File:** `docs/evaluation/datasets/pcif_final_200.jsonl`  
**Dataset Schema Version:** `1.0.0-final`  
**Total Scenarios:** 200  
**SHA-256 Checksum:** `8a8f0a659d3ca0dcd99f9557e46c85550ee4664f441f50f4646f0a93b6f585b0`

---

## 1. Validation & Integrity Summary

- **Validator Status:** `200 / 200 PASSED` (`docs/evaluation/datasets/validate_dataset.py`)
- **Schema Compliance:** 100% compliant with `docs/evaluation/datasets/pcif_dataset_schema.json`
- **PII / Clinical ID Scan:** 0 violations (all scenarios completely synthetic)
- **Diagnostic / Treatment Labels:** 0 forbidden diagnostic keys (ICD codes, prescription mandates, etc.)
- **Duplicate Checks:**
  - Exact duplicate consultation texts: **0**
  - Duplicate patient context summaries: **0**
  - Duplicate clinician notes: **0**

---

## 2. Dataset Distributions

### Domain Distribution (200 Scenarios)
| Domain | Count | Percentage |
| :--- | :---: | :---: |
| `nutrition` | 30 | 15.0% |
| `mental_wellness` | 30 | 15.0% |
| `mixed_context` | 30 | 15.0% |
| `longitudinal_change` | 30 | 15.0% |
| `conflicting_information` | 25 | 12.5% |
| `irrelevant_history` | 20 | 10.0% |
| `sparse_history` | 12 | 6.0% |
| `no_history` | 8 | 4.0% |
| `provenance_sensitive` | 15 | 7.5% |
| **Total** | **200** | **100.0%** |

*Note on Control Split:* The 20 sparse/no-history controls are partitioned exactly as 12 `sparse_history` and 8 `no_history`.

### Difficulty Distribution (200 Scenarios)
| Difficulty | Count | Percentage |
| :--- | :---: | :---: |
| `easy` | 50 | 25.0% |
| `medium` | 100 | 50.0% |
| `hard` | 50 | 25.0% |
| **Total** | **200** | **100.0%** |

---

## 3. Structural & Provenance Metrics

### Scenario-Level Provenance Coverage
- **Patient-reported only:** 81 scenarios (40.5%)
- **Clinician-authored only:** 5 scenarios (2.5%)
- **Both (Patient + Clinician):** 106 scenarios (53.0%)
- **Neither (No-History controls):** 8 scenarios (4.0%)

### Fact Unit Counts
- **Total Consultation Q Facts:** 206
- **Total Historical F Facts:** 488
  - *Patient-reported F facts:* 339
  - *Clinician-authored F facts:* 149
- **Relevant F Facts:** 460
- **Irrelevant F Facts (Distractors):** 28
- **Total Conflict Groups:** 25 (across 25 `conflicting_information` scenarios; all temporally aligned and verified)
- **Scenarios with Longitudinal History:** 60

---

## 4. Frozen Evaluation Dataset Policy

This dataset is **LOCKED and FROZEN**.

1. **No Retrospective Editing:** Do not edit scenarios, modify text, or alter gold labels after benchmark evaluation has commenced.
2. **No Model-Guided Tuning:** Do not tune PCIF prompts, architecture, or retrieval mechanisms based on final benchmark test failures.
3. **No Metric Re-definitions:** Do not alter evaluation scoring definitions after observing benchmark outcomes.
4. **Defect Documentation Policy:** If an anomaly or defect is subsequently uncovered in a scenario during or after the final 400-call evaluation, document it explicitly in an errata report. Do NOT silently repair or modify the frozen dataset.
