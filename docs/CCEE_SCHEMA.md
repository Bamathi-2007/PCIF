# Clinical Context Extraction Engine (CCEE) - Schema Specification

## Version 1.0 (Frozen Contract - Day 4 Part A)

---

## 1. Purpose and Goal

The **Clinical Context Extraction Engine (CCEE)** defines the input/output contract for extracting structured, high-value clinical context from patient conversations in PCIF.

CCEE takes conversational text from either:
* **Nutrition AI**
* **Mental Wellness AI**

and produces a compact list of clinically useful **patient-reported context items**.

> **Core Objective**: CCEE must prioritize **meaningful context compression**, not exhaustive entity extraction.

---

## 2. Frozen V1 Clinical Context Item

Each context item produced by CCEE follows this minimal JSON structure:

```json
{
  "category": "sleep",
  "summary": "Reduced sleep associated with exam stress",
  "value": "5 hours/night",
  "duration": "1 week",
  "source": "mental_wellness",
  "record_type": "patient_reported"
}
```

### 2.1 Field Specification

| Field | Type | Requirement | Description / Allowed Values |
|---|---|---|---|
| `category` | String | **Required** | One of the 11 frozen initial categories (see Section 3). |
| `summary` | String | **Required** | Concise, compressed clinical summary of the phenomenon. |
| `source` | String | **Required** | Originating agent: `"nutrition"` or `"mental_wellness"`. |
| `record_type` | String | **Required** | Verification classification: currently must be `"patient_reported"`. |
| `value` | String | *Optional* | Specific quantitative or qualitative measure (e.g., `"5 hours/night"`, `"1 glass/day"`). Omit if not reported. |
| `duration` | String | *Optional* | Timeframe or duration (e.g., `"1 week"`, `"past 3 days"`). Omit if not reported. |

> **Note on Omissions**: Unnecessary empty fields (e.g., `""` or `null`) should **not** be included merely to satisfy a template. If a detail like `value` or `duration` is not present, omit the field.

---

## 3. Allowed Sources and Categories

### 3.1 Allowed Sources
For patient-agent CCEE extractions, `source` must strictly be one of:
* `nutrition`
* `mental_wellness`

### 3.2 Record Type
For patient-agent CCEE extractions, `record_type` must currently be:
* `patient_reported`

*(Clinician-confirmed findings such as doctor notes are introduced during doctor-side workflows, not during conversational context extraction).*

### 3.3 Initial Context Categories
Do not add additional categories unless clearly required. The frozen initial categories are:

1. `nutrition` — Meal patterns, dietary habits, skipping meals.
2. `sleep` — Sleep duration, sleep quality, insomnia, waking up tired.
3. `stress` — Perceived stress levels, academic/work stress, triggers.
4. `mood` — Affect, low energy, feelings of sadness or anxiety.
5. `hydration` — Daily fluid and water intake patterns.
6. `appetite` — Reduced appetite, increased appetite, early satiety.
7. `activity` — Physical activity, exercise frequency, sedentary periods.
8. `symptom` — Patient-reported physical discomfort (e.g., fatigue, stomach discomfort, headache).
9. `habit` — Routines, caffeine consumption, lifestyle habits.
10. `lifestyle_change` — Recent schedule changes, exam periods, major routine disruptions.
11. `other_clinically_relevant_context` — Other relevant health/lifestyle factors not covered above.

---

## 4. Extraction Principles

CCEE is governed by the following core extraction principles:

1. **Store only clinically/contextually useful information**: Ignore casual greetings, weather comments, conversational filler, and non-health chit-chat.
2. **Do not save full raw conversation as clinical context**: Raw conversational turns must never be stored as clinical context items.
3. **Do not create a field for every word/entity**: Avoid creating distinct records or attributes for every noun, adjective, or mention in a sentence.
4. **Prefer one compressed record when several details describe the same phenomenon**: Synthesize interrelated clues into a single coherent clinical context item.
5. **Preserve important values such as duration or frequency only when useful**: Capture quantitative specifics (e.g., `"5 hours/night"`, `"1 week"`) when they add diagnostic or longitudinal value.
6. **Do not infer diagnoses**: CCEE captures patient-reported observations (e.g., "Reduced sleep associated with exam stress"), not medical diagnoses (do not output "Insomnia Disorder" or "Major Depressive Episode").
7. **Do not treat patient-reported information as clinically confirmed**: All items extracted from conversations are tagged with `record_type: "patient_reported"`.
8. **Ignore casual/non-health conversation**: Non-clinical remarks produce zero context items (an empty list `[]`).
9. **Related details may be combined into a meaningful summary**: Co-occurring causes and effects (e.g., exams causing stress and reduced sleep) should be summarized together when describing a single issue.
10. **Different clinically meaningful phenomena may become separate records**: If the patient discusses two distinct health issues (e.g., poor sleep in mental wellness and chronic low fluid intake in nutrition), they are captured as separate context items.

---

## 5. Canonical Compression Example

### Input Text:
> *"I've been sleeping around five hours because I'm stressed about exams for the last week."*

### Preferred Output:
```json
{
  "category": "sleep",
  "summary": "Reduced sleep associated with exam stress",
  "value": "approximately 5 hours/night",
  "duration": "1 week",
  "source": "mental_wellness",
  "record_type": "patient_reported"
}
```

### Prohibited Anti-Pattern:
Do **NOT** break this input into multiple fragmented key-value records such as:
```json
// PROHIBITED ANTI-PATTERN: DO NOT DO THIS
[
  {"entity": "sleep", "hours": 5},
  {"entity": "stress_reason", "value": "exams"},
  {"entity": "duration", "value": "1 week"}
]
```
CCEE focuses on **holistic, clinically meaningful context compression**.

---

## 6. Formal JSON Schema (Draft-07)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ClinicalContextItem",
  "description": "Minimal frozen clinical context item extracted from patient conversations.",
  "type": "object",
  "required": [
    "category",
    "summary",
    "source",
    "record_type"
  ],
  "properties": {
    "category": {
      "type": "string",
      "enum": [
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
        "other_clinically_relevant_context"
      ],
      "description": "Clinical category classification"
    },
    "summary": {
      "type": "string",
      "description": "Compressed clinical summary of the reported phenomenon"
    },
    "source": {
      "type": "string",
      "enum": [
        "nutrition",
        "mental_wellness"
      ],
      "description": "Originating conversational agent"
    },
    "record_type": {
      "type": "string",
      "enum": [
        "patient_reported"
      ],
      "description": "Clinical validation status"
    },
    "value": {
      "type": "string",
      "description": "Optional quantitative or qualitative metric (e.g., '5 hours/night')"
    },
    "duration": {
      "type": "string",
      "description": "Optional reported duration or timeframe (e.g., '1 week')"
    }
  },
  "additionalProperties": false
}
```

---

## 7. Scope Boundaries (Part A vs. Downstream Phases)

To preserve project boundaries during Day 4 Part A:
* **Included in Part A**: Minimal frozen contract for extracted conversation items (`category`, `summary`, `source`, `record_type`, optional `value` and `duration`), categories, and extraction principles.
* **Deferred to Later Days (Days 4 Part B / 5–11)**:
  * Gemini LLM prompt engineering and extraction runtime (`extract_context()`)
  * `patient_id` assignment and persistence
  * ISO timestamps (`timestamp`)
  * Database storage / MongoDB schema integration
  * Cross-session deduplication and trend detection
  * Longitudinal merging and historical conflict resolution
  * Confidence scoring
  * CCEE FastAPI endpoints
