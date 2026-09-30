# PCIF Pilot Evaluation Protocol & Methodology Specification

## 1. Experiment Objective

The **Patient Context Intelligence Framework (PCIF)** Pilot Evaluation measures the contextual extraction, historical retrieval, conflict surfacing, and provenance attribution performance of the Doctor Context Assistant under controlled synthetic conditions.

> [!IMPORTANT]
> ### Prototype & Evaluation Boundary
> 1. **Not Clinical Validation**: This evaluation benchmarks information retrieval, multi-source synthesis, and contradiction detection fidelity. It does **not** evaluate clinical treatment outcomes or diagnostic safety.
> 2. **Not Model Training Data**: PCIF is a prompt-orchestrated contextual framework and does **not** train or fine-tune neural model weights.
> 3. **Pilot Scope**: 50 scenarios evaluated under matched paired conditions (100 total invocations) to validate the evaluation pipeline before the locked 200-scenario final benchmark.

---

## 2. Experimental Design: Matched Paired Conditions

For every scenario, two matched conditions are executed against the exact same underlying model configuration:

### Condition A: Baseline (Current Consultation Only)
- **Input Provided**:
  - `[SOURCE A: CURRENT CLINICIAN CONSULTATION NOTES]` containing `current_consultation.text`.
  - `[SOURCE B: PATIENT-REPORTED CONTEXT]` is empty (`Active Profile: []`, `Longitudinal History: []`).
  - `[SOURCE C: CLINICIAN-AUTHORED HISTORICAL NOTES]` is empty (`Clinician Notes: []`).
- **Hidden Information**: Receives zero historical patient logs, zero prior clinician notes, and zero gold annotations.
- **Purpose**: Evaluates default single-encounter assistant behavior in the absence of longitudinal context.

### Condition B: PCIF (Multi-Source Longitudinal Assistance)
- **Input Provided**:
  - `[SOURCE A: CURRENT CLINICIAN CONSULTATION NOTES]` containing `current_consultation.text`.
  - `[SOURCE B: PATIENT-REPORTED CONTEXT]` containing active current patient profile and longitudinal patient-reported context records.
  - `[SOURCE C: CLINICIAN-AUTHORED HISTORICAL NOTES]` containing prior physician notes.
- **Hidden Information**: Receives zero gold annotations, zero fact IDs (`Q1`, `F1`...), zero relevance labels, zero conflict markers, and zero evaluator notes.
- **Purpose**: Evaluates whether multi-source contextual intelligence improves relevant evidence retrieval, conflict surfacing, and provenance separation while avoiding unsupported inferences.

---

## 3. Controlled Variables & Experimental Constants

To isolate the independent variable (presence vs absence of longitudinal PCIF context), all other parameters are strictly controlled:

| Parameter | Controlled Value | Description |
| :--- | :--- | :--- |
| **Foundation Model** | `gemini-3.1-flash-lite` (or configured `GEMINI_MODEL`) | Identical model checkpoint across both conditions |
| **System Instruction** | `DOCTOR_CONTEXT_SYSTEM_INSTRUCTION` | Exact production system prompt used across both conditions |
| **Response Schema** | `DoctorContextResponseSchema` | Identical 5-field structured JSON output format |
| **Sampling Temperature** | `0.0` | Deterministic greedy decoding |
| **Function Calling** | Disabled (`types.AutomaticFunctionCallingConfig(disable=True)`) | Prevents unprompted tool invocations |
| **Response Parsing** | Pydantic JSON parser | Identical schema validation and sanitization |

---

## 4. Information Hiding & Anti-Leakage Rules

1. **Evaluation Namespace Isolation**: Fact IDs (`Q1`, `Q2`..., `F1`, `F2`...), gold evidence sets (`relevant_fact_ids`, `irrelevant_fact_ids`), conflict groups (`conflict_groups`), and evaluator rationale (`notes_for_evaluator`) are evaluation metadata only. They are **never** injected into LLM prompts.
2. **Offline Read-Only Execution**: The evaluation runner does **not** write to MongoDB (`patient_context` or `doctor_notes`) and does **not** modify runtime API endpoints.
3. **Pipeline Decoupling**: Generation is fully locked in raw JSONL artifacts before scoring and metric calculation begins.

---

## 5. Metric Formulations & Mathematical Definitions

### 5.1 Relevant Historical Factor Recall
$$\text{Recall} = \frac{|\text{Retrieved Relevant Historical } F \text{ Facts}|}{|\text{Gold Relevant Historical } F \text{ Facts}|}$$
- Evaluates only historical context facts ($F$).
- Current consultation facts ($Q$) are excluded from both numerator and denominator.
- If $|\text{Gold Relevant } F \text{ Facts}| = 0$, metric is **N/A** (not 0.0% or 100.0%).

### 5.2 Omission Rate
$$\text{Omission Rate} = 1.0 - \text{Recall} = \frac{|\text{Missed Relevant Historical } F \text{ Facts}|}{|\text{Gold Relevant Historical } F \text{ Facts}|}$$
- If $|\text{Gold Relevant } F \text{ Facts}| = 0$, metric is **N/A**.

### 5.3 Irrelevant Context Inclusion Rate (Distractor Inclusion)
$$\text{Inclusion Rate} = \frac{|\text{Retrieved Irrelevant Historical } F \text{ Facts}|}{|\text{Gold Irrelevant Historical } F \text{ Facts}|}$$
- If $|\text{Gold Irrelevant } F \text{ Facts}| = 0$, metric is **N/A**.

### 5.4 Conflict Surfacing Rate
$$\text{Conflict Surfacing Rate} = \frac{|\text{Surfaced Gold Conflict Groups}|}{|\text{Gold Conflict Groups}|}$$
- A conflict group is surfaced if the response preserves both conflicting facts and identifies the discrepancy under `items_to_verify` or `context_summary`.
- If $|\text{Gold Conflict Groups}| = 0$, metric is **N/A**.

### 5.5 Unsupported Inference Rate
$$\text{Unsupported Inference Rate} = \frac{|\text{Unsupported Factual Claims Produced}|}{|\text{Total Factual Claims Produced}|}$$
- **Condition-Specific Support**:
  - For **Baseline**: Claims may only be supported by consultation $Q$ facts. If Baseline asserts historical patient reports or prior doctor findings, the claim is unsupported.
  - For **PCIF**: Claims may be supported by consultation $Q$ facts or provided historical $F$ facts.
- If $|\text{Total Factual Claims}| = 0$, metric is **N/A**.

### 5.6 Provenance Accuracy
$$\text{Provenance Accuracy} = \frac{|\text{Correctly Attributed Supported Facts}|}{|\text{Total Evaluable Attributed Facts}|}$$
- Evaluates the three provenance tiers: `current_consultation`, `patient_reported`, `clinician_authored`.
- If $|\text{Total Evaluable Attributed Facts}| = 0$, metric is **N/A**.

> [!IMPORTANT]
> ### Strict Zero-Denominator Rule
> Undefined metric values where the denominator is zero must remain **N/A** (`None` in Python) and must **never** be silently converted to 0.0% or 100.0%.

---

## 6. Semantic Matching & Adjudication Methodology

The assistant response synthesizes and paraphrases clinical context. Fact matching cannot rely solely on verbatim string equality:
1. **Semantic Content Matching**: Matches key factual elements (clinical phenomena, values, durations, status) across response sections (`relevant_current_context`, `relevant_longitudinal_changes`, `relevant_clinician_notes`, `items_to_verify`, `context_summary`).
2. **Two-Stage Verification**: Automated candidate extraction is paired with full structured scoring artifacts (`pilot_scored_results.jsonl`) exposing all matched fact IDs, supporting evidence, and provenance labels for manual inspection.

---

## 7. Provider Failure & Retry Policy

If a transient API error occurs (e.g. rate limit HTTP 429 or server HTTP 503):
- The runner applies exponential backoff across up to 3 retries.
- If an invocation fails permanently, it is recorded with `run_status: "failed"` and the specific error message.
- **Zero-Score Prevention**: Failed calls are excluded from metric calculations to prevent network failures from distorting clinical quality metrics.

---

## 8. Reproducibility & Traceability

Every evaluation run records:
- Scenario dataset filepath and record count
- Configured foundation model identifier (e.g. `gemini-3.1-flash-lite@temperature=0.0`)
- Exact system prompt SHA-256 hash
- UTC timestamp of execution
- Complete raw structured outputs in [`pilot_raw_outputs.jsonl`](file:///c:/Users/Bamathi%20G/OneDrive/Desktop/PCIF/docs/evaluation/results/pilot_raw_outputs.jsonl)
- Complete scored outputs in [`pilot_scored_results.jsonl`](file:///c:/Users/Bamathi%20G/OneDrive/Desktop/PCIF/docs/evaluation/results/pilot_scored_results.jsonl)

---

## 9. Evaluation Limitations

1. **Synthetic Scenarios**: Scenarios are systematically generated evaluation cases and do not capture real-world medical documentation messiness or human transcription typos.
2. **Non-Diagnostic**: PCIF acts as an informational context retriever, not a diagnostic engine.
3. **No Composite Score**: Component metrics are reported individually without arbitrary weighting.
