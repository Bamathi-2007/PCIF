# Clinical Context Extraction Engine (CCEE) - Schema Specification

## 1. Purpose of CCEE Schema

The **Clinical Context Extraction Engine (CCEE)** schema defines the structured JSON representation for storing patient context extracted from conversational AI interactions (Nutrition AI and Mental Wellness AI) and doctor clinical notes.

> **Status Note**: This schema provides the baseline specification for Day 1 setup and will be finalized during CCEE development (Days 4–8).

---

## 2. Minimal-Storage Principle

CCEE strictly enforces the **minimal-storage principle**:

1. **Relevance Filtering**: Do not store conversational filler, casual greetings, or non-clinical remarks.
2. **Redundancy Reduction**: Combine repetitive statements (e.g. daily logs of "slept 5 hours") into compressed longitudinal trends.
3. **Context Compression**: Store high-level clinical summaries and metrics instead of full conversational transcripts.
4. **No Schema Bloat**: Omit optional fields if no data was reported; do not generate empty placeholders.

---

## 3. Information Source Distinction

Every context item recorded in PCIF must explicitly track its origin to distinguish patient-reported conversational context from clinician-confirmed findings:

| Source Identifier | Description | Validation Status |
|---|---|---|
| `nutrition` | Extracted from Nutrition AI conversation | Patient-Reported |
| `mental_wellness` | Extracted from Mental Wellness AI conversation | Patient-Reported |
| `doctor` | Entered during doctor consultation | Clinician-Confirmed |

---

## 4. Initial Context Categories

Context records are classified into the following initial domain categories:

- `nutrition` (meal patterns, dietary changes, appetite)
- `sleep` (sleep duration, sleep quality, insomnia patterns)
- `stress` (perceived stress level, triggers)
- `mood` (emotional wellness, affect, energy)
- `activity` (physical activity, exercise habits)
- `hydration` (water intake patterns)
- `appetite` (changes in appetite or hunger cues)
- `symptom` (patient-reported discomfort or physical symptoms)
- `habit` (substance use, caffeine intake, lifestyle routines)
- `lifestyle_change` (recent major life changes impacting health)
- `other_clinically_relevant_context` (general health notes)

---

## 5. JSON Schema Representation

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ClinicalContextItem",
  "type": "object",
  "required": [
    "patient_id",
    "category",
    "summary",
    "source",
    "record_type",
    "timestamp"
  ],
  "properties": {
    "patient_id": {
      "type": "string",
      "description": "Unique identifier for the patient"
    },
    "category": {
      "type": "string",
      "description": "Clinical context category classification"
    },
    "summary": {
      "type": "string",
      "description": "Concise compressed clinical summary"
    },
    "value": {
      "type": "string",
      "description": "Specific quantitative or qualitative value (e.g., '5 hours/night')"
    },
    "duration": {
      "type": "string",
      "description": "Reported duration or temporal timeframe (e.g., 'past 2 weeks')"
    },
    "source": {
      "type": "string",
      "enum": ["nutrition", "mental_wellness", "doctor"],
      "description": "Source module that generated this record"
    },
    "record_type": {
      "type": "string",
      "enum": ["patient_reported", "doctor_confirmed"],
      "description": "Clinical verification status"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of record extraction"
    }
  }
}
```

---

## 6. Example Extracted Context Payload

```json
{
  "context": [
    {
      "patient_id": "PAT-89210",
      "category": "sleep",
      "summary": "Reduced sleep associated with exam stress",
      "value": "approximately 5 hours/night",
      "duration": "1 week",
      "source": "mental_wellness",
      "record_type": "patient_reported",
      "timestamp": "2026-09-09T23:35:00Z"
    },
    {
      "patient_id": "PAT-89210",
      "category": "nutrition",
      "summary": "Repeated breakfast skipping",
      "duration": "1 week",
      "source": "nutrition",
      "record_type": "patient_reported",
      "timestamp": "2026-09-09T23:35:00Z"
    }
  ]
}
```
