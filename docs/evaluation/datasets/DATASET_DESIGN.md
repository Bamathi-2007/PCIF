# PCIF Evaluation Dataset Design & Specification

## 1. Core Purpose & Comparative Evaluation Goal

This document defines the architecture, formal schema, scenario distribution, and validation rules for the **synthetic evaluation dataset** of the **Patient Context Intelligence Framework (PCIF)**.

> [!IMPORTANT]
> ### Crucial Operational Context
> 1. **NOT Model Training Data**: PCIF does **not** train or fine-tune machine learning models. This dataset is strictly for benchmarking and evaluating multi-source contextual assistance systems.
> 2. **Evaluation Purpose**: Creating a controlled, reproducible synthetic dataset to compare:
>    - **Condition A (Baseline)**: Current Consultation Only (Transient clinician note)
>    - **Condition B (PCIF Multi-Source Assistance)**: Current Consultation + Patient-Reported Longitudinal Context + Clinician-Authored History
> 3. **Non-Diagnostic Assistance**: PCIF assists clinicians with context retrieval and discrepancy surfacing. It does **not** generate clinical diagnoses, disease probabilities, clinical orders, or prescription directives.

---

## 2. Synthetic-Only & Privacy Policy

- **100% Synthetic Data**: All evaluation scenarios are entirely synthetic and constructed systematically for benchmarking.
- **Zero Real Patient Data**: No protected health information (PHI), real clinical encounter transcripts, electronic medical records (EMR), or real patient identifiers are used.
- **Not Medical Ground Truth**: Scenario facts, notes, and context entries are evaluation evidence representations, not real-world patient records.
- **Not Clinical Validation**: Evaluation results quantify contextual extraction and reasoning fidelity; they do not represent clinical validation of treatment outcomes.
- **No Treatment or Diagnostic Orders**: Scenarios avoid prescribing directives or medical testing orders merely for realism; historical notes focus strictly on neutral clinical history documentation (e.g., "Fatigue symptoms were reviewed during a previous consultation").

---

## 3. Dataset Splits & Leakage / Freeze Policy

The evaluation dataset is organized into two explicit splits:

| Split Name | Scenario Count | Purpose | Freeze & Modification Rules |
| :--- | :--- | :--- | :--- |
| **`pilot`** | 50 scenarios | Tooling validation & metric sanity checks | May be used to inspect failure modes, test evaluation harness scripts, and debug metric calculation tooling. |
| **`final`** | 200 scenarios | Locked benchmark for empirical study | **Strictly locked**. Must not be inspected or used to tune prompt engineering, system instructions, or heuristic thresholds. |

### Dataset Leakage Safeguards
- **Forbidden Nomenclature**: The splits are strictly termed `pilot` and `final`. Terms such as `train`, `val`, and `test` are prohibited because no model parameters are being trained.
- **Prompt Isolation**: Scenario fact IDs (`Q1`, `F1`, etc.) and gold annotations are evaluation metadata only. The runtime baseline and PCIF conditions receive only raw natural consultation text and structured CCEE/doctor notes records. Fact IDs and gold labels are **never** injected into model prompts.
- **Post-Evaluation Protocol**: If an unexpected behavior or prompt defect is uncovered during the final locked evaluation, it must be recorded as an evaluation finding rather than silently patched and re-run.

---

## 4. Scenario Schema & Data Model

Each scenario is a self-contained JSON object complying with `pcif_dataset_schema.json`:

```json
{
  "scenario_id": "SCN-PILOT-001",
  "split": "pilot",
  "domain": "longitudinal_change",
  "difficulty": "medium",
  "current_consultation": {
    "text": "Patient presents for follow-up reporting persistent daytime fatigue. Mentions trying to sleep earlier over the past week.",
    "fact_units": [
      {
        "fact_id": "Q1",
        "text": "Patient reports persistent daytime fatigue during follow-up."
      },
      {
        "fact_id": "Q2",
        "text": "Patient mentions trying to sleep earlier over the past week."
      }
    ]
  },
  "patient_reported_current_context": [
    {
      "fact_id": "F1",
      "category": "sleep",
      "summary": "Reported sleep duration improved from earlier 5 hours to 7 hours per night",
      "value": "7 hours/night",
      "duration": "past 1 week",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    }
  ],
  "patient_reported_longitudinal_history": [
    {
      "fact_id": "F2",
      "category": "sleep",
      "summary": "Reduced sleep associated with exam stress",
      "value": "5 hours/night",
      "duration": "2 weeks ago",
      "source": "mental_wellness",
      "record_type": "patient_reported",
      "status": "superseded",
      "observed_period": "2 weeks ago"
    },
    {
      "fact_id": "F3",
      "category": "hydration",
      "summary": "Low water intake during study hours",
      "value": "1 glass/day",
      "duration": "past month",
      "source": "nutrition",
      "record_type": "patient_reported",
      "status": "current"
    },
    {
      "fact_id": "F4",
      "category": "habit",
      "summary": "Prefers vegetarian meals on weekdays",
      "source": "nutrition",
      "record_type": "patient_reported",
      "status": "current"
    }
  ],
  "clinician_authored_history": [
    {
      "fact_id": "F5",
      "note": "Fatigue symptoms were reviewed during a previous consultation.",
      "record_type": "doctor_confirmed",
      "timestamp": "2026-09-15T10:00:00Z"
    }
  ],
  "gold_evidence": {
    "relevant_fact_ids": ["F1", "F2", "F3", "F5"],
    "irrelevant_fact_ids": ["F4"],
    "conflict_groups": [],
    "expected_provenance": {
      "Q1": "current_consultation",
      "Q2": "current_consultation",
      "F1": "patient_reported",
      "F2": "patient_reported",
      "F3": "patient_reported",
      "F4": "patient_reported",
      "F5": "clinician_authored"
    }
  },
  "notes_for_evaluator": "Tests recognition of longitudinal sleep transition (F2 -> F1) and low hydration (F3) relevant to fatigue, while ignoring dietary preference (F4)."
}
```

---

## 5. Input Provenance Channels

### 5.1 Source A: Current Consultation (`current_consultation`)
- Structure:
  ```json
  {
    "text": "...",
    "fact_units": [
      { "fact_id": "Q1", "text": "..." }
    ]
  }
  ```
- Represents transient, unconfirmed notes entered by the attending clinician during the visit.
- `fact_units` use the `Q` namespace (`Q1`, `Q2`...) and are **evaluation metadata only**.
- **Runtime Isolation**: Runtime baseline and PCIF conditions receive only the raw `text`. Fact IDs and annotations are never passed to the LLM.

### 5.2 Source B: Patient-Reported Context (`patient_reported_current_context` & `patient_reported_longitudinal_history`)
- Fully compatible with the frozen PCIF Clinical Context Extraction Engine (CCEE) schema:
  - `category`: Must be one of the 11 frozen CCEE categories: `nutrition`, `sleep`, `stress`, `mood`, `hydration`, `appetite`, `activity`, `symptom`, `habit`, `lifestyle_change`, `other_clinically_relevant_context`.
  - `summary`: Compressed clinical observation summary.
  - `source`: `"nutrition"` or `"mental_wellness"`.
  - `record_type`: Strictly `"patient_reported"`.
  - Optional `value` (e.g. `"5 hours/night"`) and `duration` (e.g. `"1 week"`).
- **Evaluation Metadata**:
  - `fact_id`: Stable identifier in the `F` namespace (`F1`, `F2`...).
  - `status`: Optional dataset annotation (`historical`, `current`, `superseded`).
  - `observed_period`: Optional temporal marker.
- **Longitudinal Transitions**: Represents realistic life transitions (e.g., sleep 5h → 7h, skipping breakfast → regular intake, low hydration → increased fluids). Transitions are observations and must not be automatically assumed to be clinical improvements without clinician judgment.

### 5.3 Source C: Clinician-Authored History (`clinician_authored_history`)
- Structure: `{"fact_id": "F...", "note": "...", "record_type": "doctor_confirmed", "timestamp": "..."}`
- Represents notes explicitly authored and saved by attending physicians in previous encounters.
- `record_type`: Strictly `"doctor_confirmed"`.
- Focuses on neutral historical findings (e.g. "Fatigue symptoms were reviewed during a previous consultation") without ungrounded diagnostic claims or prescription orders.
- **Prototype Boundary**: Indicates the internal PCIF provenance tier; does not imply cryptographic authentication of clinician identity.

---

## 6. Gold Evidence & Evaluation Metadata

The `gold_evidence` object establishes the objective standard against which system outputs are scored:

### 6.1 `relevant_fact_ids`
List of historical fact IDs (`F1`, `F2`...) directly pertinent to the consultation presentation.
> [!NOTE]
> `relevant_fact_ids` strictly references historical context items (`F` facts), not consultation `Q` facts.

> [!IMPORTANT]
> ### Methodological Principle: Relevance Does Not Mean Causation
> A fact labeled **`relevant`** means it is **useful contextual evidence** for the current consultation.
> It does **NOT** mean:
> - the fact caused the complaint
> - the fact is a diagnosis
> - the fact explains the symptom medically
>
> This distinction must be strictly preserved during evaluation scoring. PCIF acts as an observational context retrieval framework, not a causal diagnostic engine. Any generated claims asserting ungrounded medical causality will be penalized under **Unsupported Inference Rate**.

### 6.2 `irrelevant_fact_ids` (Distractors)
List of historical fact IDs (`F1`, `F2`...) present in the patient record that are unrelated to the current consultation. Used to compute the **Irrelevant Context Inclusion Rate**.

### 6.3 `conflict_groups` (Discrepancy Handling)
Explicitly defines multi-source discrepancies between patient-reported context, historical clinician notes, or consultation statements:

```json
{
  "conflict_id": "C1",
  "fact_ids": ["Q1", "F2"],
  "expected_behavior": "surface_for_verification",
  "description": "Consultation reports sleeping 8 hours (Q1), while previous historical context recorded 4 hours (F2)."
}
```

> [!IMPORTANT]
> ### Methodological Principle: Conflict Temporal Alignment
> A `conflict_group` may **only** represent facts that:
> 1. Refer to the **same or materially overlapping time period**, OR
> 2. **Explicitly contradict** each other.
>
> Observations from clearly different periods must be treated as **longitudinal change**, not conflict.
> *Validator Scope*: The automated validator verifies graph referential integrity, fact IDs, and expected behaviors; the dataset authoring guidelines enforce this temporal distinction.
>
> **Correct System Behavior**: The assistant must **preserve all facts** and surface the discrepancy under `items_to_verify`. It must **NOT** silently select a winner, discard either fact, or declare one source invalid.

### 6.4 `expected_provenance`
A dictionary mapping every declared fact ID (`Q` and `F`) to its expected provenance classification:
- `current_consultation` (for `Q` fact units)
- `patient_reported` (for CCEE patient context items)
- `clinician_authored` (for clinician notes)

### 6.5 `notes_for_evaluator` (Evaluator Rationale)
The `notes_for_evaluator` field records concise annotator rationale explaining subtle or ambiguous `relevant` vs `irrelevant` classifications, longitudinal transitions, and conflict setups.
- **Harness Isolation**: These rationales are evaluation-time reference metadata only. They are **never** injected into Condition A (Baseline) or Condition B (PCIF) prompts.

### 6.6 Strictly Prohibited Labels
Scenarios must **never** contain:
- Gold standard diagnostic labels (e.g., `gold_diagnosis: "Major Depressive Disorder"`)
- Disease classification codes (ICD-10, SNOMED-CT)
- Prescribed drug names, treatment directives, or testing orders
- Clinical risk probability scores

---

## 7. Scenario Domains & Difficulty Taxonomy

### 7.1 Allowed Scenario Domains

1. `nutrition`: Dietary routines, skipping meals, caffeine intake, fluid/hydration patterns.
2. `mental_wellness`: Stress triggers, mood fluctuations, sleep quality/duration, burnout.
3. `mixed_context`: Co-occurring nutrition and mental wellness context.
4. `longitudinal_change`: Explicit temporal transitions (e.g., sleep improving from 5h to 7h).
5. `conflicting_information`: Discrepant data between patient reports, doctor notes, and current visit statements.
6. `irrelevant_history`: Scenarios populated with distractor facts to evaluate selective filtering.
7. `sparse_history`: Minimal prior history (1-2 isolated facts).
8. `no_history`: Completely empty historical records (evaluates clean zero-hallucination behavior).
9. `provenance_sensitive`: Cases where distinguishing patient-reported claims from doctor-confirmed findings is essential.

### 7.2 Difficulty Rating Criteria

Difficulty reflects **contextual reasoning complexity**, NOT medical trivia:

- **`easy`**: Small number of facts (1–3), high relevance, direct keyword alignment, zero or minimal distractors.
- **`medium`**: Moderate number of facts (4–7), mix of relevant items and distractor items across 2 sources, requiring filtering.
- **`hard`**: Rich multi-source context (6–10+ facts), temporal shifts, superseded history, explicit conflict groups, and distractor noise.

---

## 8. Pilot & Final Dataset Distribution Plan

### 8.1 Pilot Dataset (50 Scenarios)
Used for validating testing harnesses, format parsers, and evaluation metric scripts.

| Domain Family | Target Count | Difficulty Distribution |
| :--- | :--- | :--- |
| `nutrition` | 8 | 2 Easy, 4 Medium, 2 Hard |
| `mental_wellness` | 8 | 2 Easy, 4 Medium, 2 Hard |
| `mixed_context` | 8 | 2 Easy, 4 Medium, 2 Hard |
| `longitudinal_change` | 7 | 1 Easy, 4 Medium, 2 Hard |
| `conflicting_information` | 6 | 1 Easy, 3 Medium, 2 Hard |
| `irrelevant_history` | 5 | 1 Easy, 3 Medium, 1 Hard |
| `sparse_history` / `no_history` | 5 | 3 Easy, 2 Medium, 0 Hard |
| `provenance_sensitive` | 3 | 0 Easy, 2 Medium, 1 Hard |
| **Total** | **50** | **12 Easy (24%), 26 Medium (52%), 12 Hard (24%)** |

### 8.2 Final Evaluation Dataset Plan (200 Scenarios)
To be generated and locked prior to final comparative evaluation.

| Domain Family | Target Count | Target Difficulty Split |
| :--- | :--- | :--- |
| `nutrition` | 30 | ~8 Easy, 15 Medium, 7 Hard |
| `mental_wellness` | 30 | ~8 Easy, 15 Medium, 7 Hard |
| `mixed_context` | 30 | ~7 Easy, 16 Medium, 7 Hard |
| `longitudinal_change` | 30 | ~7 Easy, 15 Medium, 8 Hard |
| `conflicting_information` | 25 | ~6 Easy, 12 Medium, 7 Hard |
| `irrelevant_history` | 20 | ~5 Easy, 10 Medium, 5 Hard |
| `sparse_history` / `no_history` | 20 | ~14 Easy, 6 Medium, 0 Hard |
| `provenance_sensitive` | 15 | ~3 Easy, 8 Medium, 4 Hard |
| **Total** | **200** | **50 Easy (25%), 100 Medium (50%), 50 Hard (25%)** |

---

## 9. Formal Metric Definitions & Zero-Denominator Handling

Once scenarios are evaluated under Condition A and Condition B, the harness computes:

1. **Relevant Historical Factor Recall**:
   $$\text{Recall} = \frac{|\text{Retrieved Relevant Historical Facts}|}{|\text{Gold Relevant Historical Facts } (F)|}$$
   - Evaluates only historical gold facts ($F$).
   - If $|\text{Gold Relevant Facts}| = 0$, metric is **N/A**.

2. **Omission Rate**:
   $$\text{Omission Rate} = 1 - \text{Recall} = \frac{|\text{Missed Relevant Historical Facts}|}{|\text{Gold Relevant Historical Facts } (F)|}$$
   - If $|\text{Gold Relevant Facts}| = 0$, metric is **N/A**.

3. **Unsupported Inference Rate**:
   $$\text{Unsupported Inference Rate} = \frac{|\text{Unsupported Factual Claims Produced}|}{|\text{Total Factual Claims Produced}|}$$
   - Denominator is the count of factual claims generated by the system (not total textual sentences).
   - If $|\text{Total Factual Claims Produced}| = 0$, metric is **N/A** (not 0%).

4. **Provenance Accuracy**:
   $$\text{Provenance Accuracy} = \frac{|\text{Facts with Correct Provenance Attribution}|}{|\text{Total Attributed Facts}|}$$
   - Evaluates all three classes: `current_consultation`, `patient_reported`, and `clinician_authored`.
   - If $|\text{Total Attributed Facts}| = 0$, metric is **N/A**.

5. **Conflict Surfacing Rate**:
   $$\text{Conflict Surfacing Rate} = \frac{|\text{Surfaced Discrepancies Matching Gold Conflicts}|}{|\text{Gold Conflict Groups}|}$$
   - If scenario has no gold conflicts ($|\text{Gold Conflicts}| = 0$), metric is **N/A** (not 0%).

6. **Irrelevant Context Inclusion Rate**:
   $$\text{Irrelevant Inclusion Rate} = \frac{|\text{Retrieved Irrelevant Facts}|}{|\text{Gold Irrelevant Historical Facts } (F)|}$$
   - If scenario has no distractor facts ($|\text{Gold Irrelevant Facts}| = 0$), metric is **N/A** (not 0%).

> [!IMPORTANT]
> **Zero-Denominator Rule**: When the denominator is zero, the metric must remain **N/A** and must **never** be silently converted to 0.0% or 100.0%.

---

## 10. Dataset Validation Protocol

Validation is automated via [`validate_dataset.py`](file:///c:/Users/Bamathi%20G/OneDrive/Desktop/PCIF/docs/evaluation/datasets/validate_dataset.py).

To execute the validator:
```bash
python docs/evaluation/datasets/validate_dataset.py docs/evaluation/datasets/
```

### Checks Enforced:
1. Validates top-level schema conformance and field requirements.
2. Checks uniqueness of `scenario_id` across the entire dataset.
3. Enforces domain and difficulty enumerations.
4. Checks uniqueness of `Q` fact IDs within the consultation and `F` fact IDs within historical context.
5. Verifies all `relevant_fact_ids` and `irrelevant_fact_ids` reference declared historical `F` facts only.
6. Verifies that `relevant_fact_ids` and `irrelevant_fact_ids` are completely disjoint.
7. Ensures `conflict_groups` reference valid declared facts (`Q` and/or `F`) and have `expected_behavior: "surface_for_verification"`.
8. Verifies `expected_provenance` maps accurately to declared origins (`current_consultation`, `patient_reported`, `clinician_authored`).
9. Enforces CCEE category and source rules for patient-reported records.
10. Scans for forbidden PII patterns and forbidden diagnostic/order labels.
