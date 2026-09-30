# PCIF Evaluation Tooling & Methodology Freeze

**Freeze Date:** 2026-09-30  
**Harness Version:** `2.0.0-final`  
**Dataset Reference:** `docs/evaluation/datasets/pcif_final_200.jsonl`  
**Dataset SHA-256:** `8a8f0a659d3ca0dcd99f9557e46c85550ee4664f441f50f4646f0a93b6f585b0`

---

## 1. Experimental Conditions

### Condition A: Baseline (Consultation-Only)
- **Input Supplied:** `current_consultation.text` (transient consultation transcript).
- **Hidden / Withheld Context:** Patient-reported context (`Source B`), longitudinal history (`Source B`), clinician-authored notes (`Source C`), gold evidence, fact IDs, and evaluator rationales are strictly withheld.
- **Scoring Boundary:** Baseline is scored on consultation support and explicit provenance. Hidden historical $F$ facts are treated as unavailable evidence; speculative resemblance to hidden history does not receive retrieval credit and is classified as unsupported unless grounded in consultation evidence $Q$.

### Condition B: PCIF (Context-Synthesized)
- **Input Supplied:** `current_consultation` + synthesized patient-reported context (`Source B`) + longitudinal context (`Source B`) + clinician-authored history (`Source C`).
- **Scoring Boundary:** Scored across historical recall, irrelevant inclusion filtering, multi-tier provenance accuracy, conflict detection, and unsupported inference suppression.

---

## 2. Frozen Metric Definitions & N/A Policies

### 1. Historical Fact Recall (Relevant Evidence)
$$\text{Recall} = \frac{|\text{Retrieved Relevant } F \text{ Facts}|}{|\text{Total Gold Relevant } F \text{ Facts}|}$$
- *Condition Behavior:* Evaluated on PCIF. For Baseline, historical $F$ evidence is withheld, so historical retrieval is not evaluable / treated as unsupplied context.

### 2. Irrelevant Context Inclusion (Distractor Intrusion)
$$\text{Inclusion Rate} = \frac{|\text{Included Irrelevant } F \text{ Facts}|}{|\text{Total Gold Irrelevant } F \text{ Facts}|}$$
- Quantifies distractor filtering precision across scenarios containing explicit distractors.

### 3. Conflict Surfacing Rate & Condition-Aware N/A Rule
$$\text{Conflict Surfacing Rate} = \frac{|\text{Surfaced Conflicts}|}{|\text{Evaluable Gold Conflicts}|}$$
- **Evaluability Rule:** For any condition, conflict scoring uses *only* conflicts whose required constituent facts were actually supplied to that condition.
- **Baseline N/A Policy:** If a gold conflict requires historical $F$ evidence not supplied to Baseline, denominator = 0, returning `None` / `N/A` (rather than 0%). Conditions are never penalized for evidence intentionally withheld.

### 4. Provenance Attribution Accuracy & Channel Breakdown
Evaluated on supported factual claims using the 4-tier taxonomy: `correct`, `incorrect`, `not_explicit`, `not_applicable`.
- **Overall Provenance Accuracy:**
  $$\text{Accuracy} = \frac{\text{correct}}{\text{correct} + \text{incorrect}}$$
- **Channel-Specific Accuracies:**
  - $A_{\text{consultation}} = \frac{\text{correct}_{\text{consultation}}}{\text{correct}_{\text{consultation}} + \text{incorrect}_{\text{consultation}}}$
  - $A_{\text{patient}} = \frac{\text{correct}_{\text{patient}}}{\text{correct}_{\text{patient}} + \text{incorrect}_{\text{patient}}}$
  - $A_{\text{clinician}} = \frac{\text{correct}_{\text{clinician}}}{\text{correct}_{\text{clinician}} + \text{incorrect}_{\text{clinician}}}$
- **Provenance Explicitness Rate:**
  $$\text{Explicitness Rate} = \frac{\text{correct} + \text{incorrect}}{\text{correct} + \text{incorrect} + \text{not\_explicit}}$$
  *(Unsupported claims are never credited as provenance-correct merely for bearing a label.)*

### 5. Unsupported Factual Inference Rate
$$\text{Unsupported Rate} = \frac{|\text{Unsupported Factual Claims}|}{|\text{Total Factual Claims Generated}|}$$

---

## 3. Tooling Validation & Execution Policy

- **Unit Test Suite:**
  - `tests/test_evaluation_metrics.py`: 6/6 tests passing
  - `tests/test_dataset_validator.py`: 5/5 tests passing
  - Combined metric & validator tests: 11/11 passing
- **Dataset Validator:** `docs/evaluation/datasets/validate_dataset.py` validates all 200 scenarios with zero errors.
- **Zero Final Calls Commitment:** No final Gemini API calls have been made on the 200-scenario dataset on this machine. Execution of the 400-call benchmark is reserved for the designated evaluation environment.
