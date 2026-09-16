# CCEE Evaluation Report: Component-Level Synthetic Evaluation

**Date:** September 2026  
**System Component:** Clinical Context Extraction Engine (CCEE)  
**Project:** Patient Context Intelligence Framework (PCIF) Prototype  
**Scope Phase:** Day 8 – Final CCEE Evaluation, Hardening & Contract Freeze  

> **Research Context & Mandatory Framing Disclaimer**: This document presents a **component-level prototype evaluation on controlled synthetic conversational cases**. This evaluation measures structural schema compliance, semantic relevance filtering, context compression, and evidence fidelity under synthetic research scenarios. It does **NOT** represent clinical validation, medical accuracy validation, physician adjudication, hospital testing, real-patient evaluation, or production readiness. All percentages report performance solely on the synthetic test set documented herein.

---

## A. Evaluation Objective

The objective of this evaluation is to evaluate whether the Clinical Context Extraction Engine (CCEE) reliably enforces the frozen `ClinicalContextItem` schema and core extraction principles developed during Days 4–7 prior to shared database integration on Days 9–11.

Specifically, CCEE aims to maximize:
$$\text{Supported Useful Context Retained}$$
while minimizing:
$$\text{Irrelevant Content} + \text{Redundancy} + \text{Unsupported Inference} + \text{False Precision}$$

The core research hypothesis of PCIF is **NOT** that "more patient data automatically improves diagnosis accuracy", but that:
> *"Relevant longitudinal patient context may improve contextual completeness and the quality of downstream clinical decision support compared with isolated-session information."*

---

## B. Evaluation Setup

- **Extraction Architecture**: Single-pass LLM structured extraction using Google Gemini via the `google-genai` SDK with JSON Schema enforcement (`response_mime_type="application/json"`, `response_schema=CCEEExtractionResult`, `temperature=0.0`).
- **Engine Layer**: `ccee.engine.ClinicalContextExtractionEngine` wrapping `backend.app.services.llm_service.GeminiLLMService`.
- **Validation & Hardening Controls**: Pydantic container validation (`ExtractedItem`), strict dataclass enforcement (`ClinicalContextItem`), non-empty summary validation, and deterministic deduplication (`_deduplicate_items`).
- **Test Execution Suite**: Automated evaluation script (`tests/test_day8_ccee_evaluation.py`) executing local schema contract/hardening checks (Phase 1) and live LLM semantic evaluations (Phase 2).
- **Rate-Limit & Infrastructure Policy**: Paced evaluation (3.5s delay between calls) with exponential backoff retries. API infrastructure failures raise explicit exceptions rather than returning empty context lists (`[]`).

---

## C. Evaluation Dimensions

The framework evaluates 11 independent, component-level semantic dimensions. Each dimension is evaluated independently per test case so that a failure in one specific assertion does not falsely reduce scores for unrelated passing dimensions.

| # | Evaluation Dimension | Key Research Question |
|---|---|---|
| **1** | **Relevance Filtering** | Did irrelevant content (greetings, weather, preferences, hypotheticals, third-person reports, negated symptoms) correctly yield an empty context list `[]`? |
| **2** | **Relevant Context Retention** | Was clinically and contextually useful patient-reported information preserved without unnecessary information loss? |
| **3** | **Compression / Redundancy Control** | Were repeated descriptions of one phenomenon consolidated into minimal records without key-value bloat or cause-only over-extraction? |
| **4** | **Distinct Phenomenon Preservation** | Were genuinely separate health phenomena kept as distinct structured records? |
| **5** | **Unsupported Inference Prevention** | Did CCEE avoid inferring clinical diagnoses (e.g., "Insomnia", "Depression") or unstated cause-and-effect relationships? |
| **6** | **Evidence Preservation** | Were reported quantities, durations, cautious qualifiers ("about", "some days"), and explicit negations represented faithfully? |
| **7** | **Temporal Reasoning** | Did CCEE correctly process current vs. past state, ongoing durations, explicit self-corrections, and resolved past events? |
| **8** | **Speaker Attribution Safety** | Were Assistant questions and hypotheses strictly excluded from patient self-report evidence? |
| **9** | **Source Integrity** | Did the `source` field remain strictly tied to the originating agent stream (`nutrition` or `mental_wellness`) regardless of extracted category? |
| **10** | **Schema Validity** | Did every returned item strictly conform to the frozen `ClinicalContextItem` contract without extra or invalid fields? |
| **11** | **Context Sufficiency** | Did the compressed representation preserve enough meaningful context for downstream clinical decision support? |

---

## D. Test-Set Composition

The synthetic test set consists of **36 controlled test cases** developed across Days 4–8:

- **Day 4 Baseline Cases (5 cases)**: Contract validation, basic relevance filtering, meal skipping, sleep reduction, appetite change, low water intake, and casual weather conversation.
- **Day 5 Boundary Edge Cases (5 cases)**: Casual greetings, non-clinical color preference, multi-phenomenon extraction, diagnosis prevention, and uncertain self-reports.
- **Day 6 Compression Cases (7 cases)**: Repeated sleep statements, cause/trigger folding, distinct phenomenon separation, nutrition repetition, hydration uncertainty preservation, independent stress, and irrelevant repetition.
- **Day 7 Temporal Cases (9 cases)**: Explicit self-correction, past-to-current improvement, ongoing duration, resolved historical events, worsening appetite with approximate duration, temporal decline, distinct temporal trajectories, source integrity cross-domain, and multi-turn transcript handling.
- **Day 8 Hardening Cases (10 cases)**: Hypothetical health inquiries, third-person roommate reports, mixed relevant/irrelevant text, explicit negation, negated candidate + real issue, corrected quantity, unsupported causal inference, assistant hypothesis rejection, whitespace input, and invalid source validation.

---

## E. Evaluation Results

### Overall Case Pass Rate

$$\text{Overall Case Pass Rate} = \frac{\text{Fully Passing Test Cases}}{\text{Total Evaluated Test Cases}} = \frac{36}{36} = 100.0\%$$

- **Total Semantic Test Cases Evaluated**: 36
- **Fully Passed Cases**: 36
- **Failed Cases**: 0
- **Inconclusive (API Outage/Rate-Limit)**: 0

---

### Independent Dimension Results Table

Each dimension is evaluated independently using its **applicable test cases** as the denominator:

| Evaluation Dimension | Passed Cases / Applicable Cases | Pass Rate (%) |
|---|:---:|:---:|
| **1. Relevance Filtering** | 35 / 35 | **100.0%** |
| **2. Relevant Context Retention** | 35 / 35 | **100.0%** |
| **3. Compression / Redundancy Control** | 35 / 35 | **100.0%** |
| **4. Distinct Phenomenon Preservation** | 35 / 35 | **100.0%** |
| **5. Unsupported Inference Prevention** | 36 / 36 | **100.0%** |
| **6. Evidence Preservation** | 36 / 36 | **100.0%** |
| **7. Temporal Reasoning** | 36 / 36 | **100.0%** |
| **8. Speaker Attribution Safety** | 36 / 36 | **100.0%** |
| **9. Source Integrity** | 36 / 36 | **100.0%** |
| **10. Schema Validity** | 36 / 36 | **100.0%** |
| **11. Context Sufficiency** | 35 / 35 | **100.0%** |

*Note: Case 8.10 (`source: "fitness_ai"`) is a local API parameter validation test that expects a `ValueError`. It is not a conversational extraction case, so it is excluded from conversation-specific extraction dimension denominators (Relevance Filtering, Relevant Context Retention, Compression, Distinct Phenomenon Preservation, Context Sufficiency).*

---

## F. Verification of Micro-Fixes & Regression Resolutions

All previously observed semantic edge-case mismatches have been resolved and verified:

1. **Cause-Only Stress Folding (Resolved)**:
   - *Input*: `"I've been skipping meals this week and sleeping only four hours because I'm stressed about exams."`
   - *Verified Behavior*: Emitted **exactly 2 items** (`nutrition: skipping meals` and `sleep: 4 hours/night` folding exam stress into sleep summary). Cause-only exam stress created **zero** 3rd standalone stress records.
2. **Temporal Attribute Attachment (Resolved)**:
   - *Input*: `"I'm sleeping only four hours and I've also lost my appetite this week."`
   - *Verified Behavior*: Emitted 2 items (`sleep: 4 hours/night`, `duration: None` and `appetite: loss of appetite`, `duration: "this week"`). The temporal modifier `"this week"` attaches strictly to appetite and is **NOT** inherited by sleep.
3. **Unsupported Causal Inference Prevention (Resolved)**:
   - *Input*: `"I've been tired lately and I also haven't been sleeping much."`
   - *Verified Behavior*: Preserved both tiredness and reduced sleep without making an unstated causal claim ("sleep deprivation caused fatigue").
4. **Assistant Hypothesis Rejection (Resolved)**:
   - *Transcript*: User: *"I've been tired lately."* / Assistant: *"Could this be because you're sleeping four hours?"* / User: *"No, I usually sleep around seven hours."*
   - *Verified Behavior*: Extracted User facts (`sleep: ~7 hours/night` and `symptom: tired`). Assistant hypothesis (`4 hours`) strictly rejected.



---

## G. Day 8 Hardening Verification Results

The 10 Day 8 synthetic adversarial cases yielded the following verified behavioral outcomes:

1. **CASE 1 (Hypothetical health statement)**: `"What happens if someone sleeps only three hours every night?"`  
   *Result*: `[]`. Hypothetical inquiry correctly recognized as non-patient report. No sleep record created. (Passed)
2. **CASE 2 (Third-person information)**: `"My roommate barely sleeps four hours because of exams."`  
   *Result*: `[]`. Third-party report correctly ignored. No patient record created. (Passed)
3. **CASE 3 (Mixed relevant + irrelevant info)**: `"My favourite colour is yellow. Anyway, I've been sleeping only five hours lately because of assignments."`  
   *Result*: `[1 item]`. Extracted 1 sleep item (`value: "5 hours/night"`, `summary: "Reduced sleep associated with assignment workload"`). Favourite color preference ignored. (Passed)
4. **CASE 4 (Explicit negation)**: `"I am not having any appetite problems. I'm eating normally."`  
   *Result*: `[]`. Explicitly denied appetite problem correctly produced no active record. (Passed)
5. **CASE 5 (Negated candidate followed by real issue)**: `"I'm not skipping meals, but I barely drink water during college."`  
   *Result*: `[1 item]`. Extracted 1 hydration record (`summary: "Low water intake during college hours"`). Negated meal skipping created no record. (Passed)
6. **CASE 6 (Corrected quantity)**: `"I drink maybe one glass of water a day — actually that's not right, probably closer to four glasses."`  
   *Result*: `[1 item]`. Extracted 1 hydration item (`value: "approximately 4 glasses/day"`). Superseded 1 glass/day figure discarded. (Passed)
7. **CASE 7 (Unsupported causal inference)**: `"I've been tired lately and I also haven't been sleeping much."`  
   *Result*: Extracted both tiredness (`symptom`) and reduced sleep (`sleep`) without inferring an unstated causal claim ("reduced sleep caused fatigue"). No medical diagnosis inferred. (Passed)
8. **CASE 8 (Assistant hypothesis rejection)**: User: `"I've been tired lately."` / Assistant: `"Could this be because you're only sleeping four hours?"` / User: `"No, I usually sleep around seven hours."`  
   *Result*: Extracted user statement (`sleep: around 7 hours/night`) and tiredness (`symptom`). Assistant hypothesis (4 hours) rejected. (Passed)
9. **CASE 9 (Empty/whitespace input)**: `"   "`  
   *Result*: `[]`. Engine pre-filtering immediately returned empty list without making an LLM API call. (Passed)
10. **CASE 10 (Invalid source validation)**: `source: "fitness_ai"`  
    *Result*: Rejection via controlled `ValueError: Invalid source 'fitness_ai'`. Source stream preserved without silent rewriting. (Passed)

---

## H. Failure Handling & Schema Validation Rules

### 1. Invariant Failure Handling
The system strictly enforces the following state invariants:
- **Irrelevant Patient Conversation** $\rightarrow$ Returns empty list `[]` (Meaning: "No clinically relevant patient context identified").
- **Empty / Whitespace Input** $\rightarrow$ Returns empty list `[]` locally in 0ms without invoking the LLM API.
- **Missing API Key / Infrastructure Error** $\rightarrow$ Raises explicit `RuntimeError` exception. Provider failures are **NEVER** swallowed as `[]`.
- **Invalid Source / Category** $\rightarrow$ Raises explicit `ValueError` exception. Unrecognized inputs are **NEVER** silently rewritten.
- **Malformed Top-Level Response / Unparsable JSON** $\rightarrow$ Raises controlled `RuntimeError` extraction failure.
- **Result Containing Only Schema-Invalid Items** $\rightarrow$ Raises controlled `RuntimeError` extraction failure ("All candidate items failed schema validation"). Must **NOT** return `[]` because `[]` signifies no relevant context was identified.

### 2. Partial Malformed Output Handling
If an LLM response emits multiple candidate items where some are valid and others are schema-invalid (e.g., mixed valid + invalid candidate items):
- Valid items are retained and serialized.
- Schema-invalid items are rejected with warning log entries.
- This is documented as **partial validation**. The system does not fabricate replacement context or pretend the full response was perfect.

### 3. Schema Invariants
`ClinicalContextItem` schema remains strictly frozen:
- `category` (string, required: one of 11 allowed categories)
- `summary` (string, required: non-empty string)
- `source` (string, required: `"nutrition"` or `"mental_wellness"`)
- `record_type` (string, required: `"patient_reported"`)
- `value` (string, optional)
- `duration` (string, optional)

**No schema expansion or extra fields have been added.**

---

## I. Scope Boundaries & Research Disclaimers

To maintain strict research framing:
1. **Synthetic Data Only**: All evaluation cases are controlled synthetic conversational scenarios.
2. **No Real Patient Data**: No real patient health records or PHI were used or submitted to external API services.
3. **No Clinician Adjudication**: Extractions were evaluated against synthetic ground truth contracts, not adjudicated by a medical panel.
4. **No EHR / Hospital Deployment**: CCEE is an experimental research component for decision-support prototyping.
5. **No Medical Diagnosis**: CCEE does not diagnose diseases or evaluate diagnostic accuracy.
6. **No Clinical Outcome Claims**: Metrics report synthetic semantic case pass rates, not medical efficacy or clinical treatment outcomes.
7. **Longitudinal Persistence Deferred**: Multi-session longitudinal merging, cross-session deduplication, and database persistence begin on Days 9–11.

---

## J. Downstream Research Objective (Days 12–15 Direction)

During Days 12–15 (Doctor-Side System Development), PCIF will conduct a comparative decision-support evaluation comparing:

- **BASELINE CONDITION**:  
  Doctor-side AI Assistant receives **ONLY current consultation input**.
- **PCIF CONTEXT CONDITION**:  
  Doctor-side AI Assistant receives **current consultation input + relevant longitudinal CCEE patient context**.

Planned research evaluation dimensions for Days 12–15:
- Contextual completeness of doctor-side AI summaries.
- Relevant historical risk factor retrieval.
- Omission rate of multi-week lifestyle changes.
- Unsupported clinical assumption rate.

*Note: Superior performance of the longitudinal context condition will not be claimed until experimentally demonstrated during Days 12–15.*

---

## K. Summary and Freeze Recommendation

The Clinical Context Extraction Engine (CCEE) demonstrates:
- **100.0% Synthetic Case Pass Rate** (36/36 semantic cases fully passing).
- **100% Schema Validity, Source Integrity, Evidence Preservation, Speaker Attribution Safety, Temporal Reasoning, and Unsupported Inference Prevention**.
- Fail-safe handling of invalid input parameters, malformed top-level responses, all-invalid candidate items, and infrastructure failures.

**Recommendation**: CCEE is stable, verified, and hardened. **CCEE is frozen and ready to move to Day 9 Shared Database Integration.**
