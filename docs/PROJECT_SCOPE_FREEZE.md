# PCIF – Patient Context Intelligence Framework

## Project Scope Freeze – Version 1.0

**Date:** September 2026
**Project Type:** Healthcare AI Research Prototype
**Development Duration:** 20 Days

---

## 1. Project Vision

PCIF is a healthcare AI framework designed to preserve meaningful information about a person's **physical/lifestyle health and mental wellness over time** and make that information available to a doctor when required.

The system does **not** aim to replace doctors or autonomously diagnose patients.

Its purpose is to provide doctors with better longitudinal patient context that may not normally be available during a short clinical consultation.

The final medical interpretation and decision always belongs to the doctor.

---

# 2. Core Problem

A doctor usually sees a patient during a limited consultation period.

However, many health-related changes happen outside the hospital, such as:

* changes in sleep,
* stress,
* appetite,
* meal patterns,
* hydration,
* physical activity,
* mood,
* lifestyle habits,
* recurring discomfort,
* changes occurring over several weeks or months.

Patients may forget these details, may not consider them important, or may not explain their complete lifestyle history during consultation.

At the same time, permanently storing entire AI conversations would create:

* excessive data,
* duplicated information,
* irrelevant conversational text,
* privacy concerns,
* difficult clinical interpretation.

PCIF therefore focuses on storing **only meaningful clinical context extracted from patient conversations**.

---

# 3. Core System Idea

The patient-facing website contains two separate conversational AI systems:

### 3.1 Nutrition AI

Handles conversations primarily related to:

* food habits,
* meal patterns,
* appetite,
* hydration,
* nutrition,
* physical lifestyle,
* activity-related context,
* other relevant physical-health lifestyle factors.

---

### 3.2 Mental Wellness AI

Handles conversations primarily related to:

* mood,
* stress,
* sleep,
* anxiety-related experiences,
* emotional wellness,
* behavioural changes,
* mental-wellness-related lifestyle context.

---

Both systems exist inside the **same website** but remain separate so their conversations can be more domain-specific and personalized.

They belong to the same patient account.

---

# 4. Shared Patient Context

The Nutrition AI and Mental Wellness AI do not maintain completely independent health histories.

Both contribute clinically relevant information to the **same longitudinal patient context database**.

Example:

A patient's Mental Wellness conversation may identify:

* increased stress,
* reduced sleep.

A Nutrition conversation may identify:

* breakfast skipping,
* reduced appetite.

Instead of treating these as unrelated conversations, PCIF keeps them under the same patient so that their relationship can later be considered.

---

# 5. Clinical Context Extraction Engine – CCEE

The **Clinical Context Extraction Engine (CCEE)** is one of the main components of the project.

Its responsibility is to process patient conversations and identify only the information that may be clinically or contextually useful.

## CCEE IS NOT

CCEE is not intended to:

* save every sentence,
* save the entire conversation,
* extract every possible keyword,
* create many database values from every sentence,
* preserve unnecessary conversational details.

For example, one sentence may technically contain eight possible entities.

PCIF should **not automatically create eight database fields simply because they exist**.

---

# 6. CCEE Main Principle

CCEE should perform:

**Conversation**

↓

**Clinical relevance identification**

↓

**Redundancy reduction**

↓

**Context compression**

↓

**Structured clinical representation**

↓

**Database storage**

The objective is:

> Store the minimum amount of information required to preserve meaningful patient context.

---

# 7. Example

Patient says:

> "I've been sleeping only around five hours these days because I'm stressed about exams. I also skipped breakfast several times this week."

The complete sentence should not be stored as permanent clinical history.

A possible CCEE output is:

```json
{
  "context": [
    {
      "category": "sleep",
      "summary": "Reduced sleep associated with increased stress",
      "value": "approximately 5 hours",
      "duration": "recent",
      "source": "mental_wellness"
    },
    {
      "category": "nutrition",
      "summary": "Repeated breakfast skipping",
      "duration": "1 week",
      "source": "nutrition"
    }
  ]
}
```

The exact schema may evolve during CCEE development, but the **minimal-storage principle must not change**.

---

# 8. CCEE Data Rules

Every extracted record should be evaluated using the following questions:

### Rule 1 – Is it clinically relevant?

If not, do not store it.

### Rule 2 – Does the same information already exist?

If yes, avoid unnecessary duplicate records.

### Rule 3 – Is this a meaningful change?

Changes and trends are more useful than repetitive statements.

Example:

Instead of storing:

```text
Monday: slept 5 hours
Tuesday: slept 5 hours
Wednesday: slept 5 hours
```

the system should preferably represent:

```text
Persistent reduced sleep of approximately 5 hours/night
```

where appropriate.

### Rule 4 – Can the information be compressed without losing clinical meaning?

If yes, store the compressed representation.

### Rule 5 – Do not assume patient-reported information is medically confirmed.

Patient conversations represent **patient-reported context**.

Doctor-confirmed information must be distinguishable from AI-extracted patient context.

---

# 9. Initial CCEE Context Categories

The initial prototype may use categories such as:

```text
nutrition
sleep
stress
mood
activity
hydration
appetite
symptom
habit
lifestyle_change
other_clinically_relevant_context
```

These categories can be refined during development.

The system should not create categories unnecessarily.

---

# 10. Initial CCEE JSON Structure

The initial structure for an extracted context item is:

```json
{
  "patient_id": "PATIENT_ID",
  "category": "sleep",
  "summary": "Reduced sleep associated with increased stress",
  "value": "approximately 5 hours",
  "duration": "1 week",
  "source": "mental_wellness",
  "record_type": "patient_reported",
  "timestamp": "TIMESTAMP"
}
```

Not every field has to contain a value.

Unnecessary empty data should not be generated merely to satisfy the schema.

---

# 11. Shared Database

PCIF uses one shared patient-context database.

For Version 1, the primary database is planned to be:

**MongoDB**

The database should associate all context with a unique patient identifier.

Initial logical collections:

```text
users
patient_context
doctor_notes
```

---

# 12. Patient Context Storage

Example conceptual structure:

```text
Patient
│
├── Basic Profile
│
├── Nutrition Context
│
├── Mental Wellness Context
│
├── Lifestyle Context
│
└── Doctor-Confirmed Information
```

The database must preserve the source of information.

For example:

```text
source = nutrition
source = mental_wellness
source = doctor
```

This prevents patient-reported AI-extracted information from being confused with clinician-confirmed findings.

---

# 13. Longitudinal Context

The purpose of storing the information is not simply to create a database.

The important feature is **longitudinal context**.

The system should eventually allow statements such as:

```text
Stress increased during the previous month.
Sleep duration decreased during the same period.
Breakfast skipping was reported repeatedly.
Appetite reduction appeared later.
```

This historical context can become useful during doctor consultation.

---

# 14. Doctor-Side System

The doctor uses a separate doctor-facing AI interface within the system.

The doctor should be able to:

1. Search/select a patient.
2. Retrieve previous patient context.
3. View meaningful lifestyle and wellness history.
4. Ask questions regarding the available context.
5. Add information from the current consultation.
6. Add relevant clinical observations or confirmed findings.
7. Discuss available information with the AI assistant.
8. Make the final medical decision independently.

---

# 15. Doctor AI Responsibilities

The doctor-side AI should primarily perform:

### Retrieve

Retrieve relevant historical context belonging to the selected patient.

### Summarize

Convert longitudinal history into information that is easy for the doctor to review.

### Correlate

Highlight potentially relevant relationships between historical information and the current consultation.

### Assist

Answer the doctor's questions based on available patient context.

---

# 16. Doctor AI Limitations

The doctor AI must NOT be designed as:

* an autonomous doctor,
* an independent diagnosis system,
* a replacement for clinical judgement,
* a system claiming to diagnose every disease,
* a system that makes treatment decisions independently.

The system provides **decision support**.

The doctor provides **clinical judgement**.

---

# 17. Doctor Consultation Flow

```text
Doctor Login
      ↓
Search / Select Patient
      ↓
Retrieve Longitudinal Patient Context
      ↓
Current Patient Consultation
      ↓
Doctor Adds Relevant Information
      ↓
Doctor AI Reviews Available Context
      ↓
AI-Assisted Discussion
      ↓
Doctor Interpretation
      ↓
FINAL CLINICAL DECISION
```

---

# 18. Complete PCIF V1 Data Flow

```text
                         PATIENT
                            │
                     Patient Account
                            │
               ┌─────────────┴─────────────┐
               │                           │
               ▼                           ▼
         Nutrition AI              Mental Wellness AI
               │                           │
               └─────────────┬─────────────┘
                             │
                             ▼
                            CCEE
                             │
                 Clinical Relevance Filtering
                             │
                   Redundancy Reduction
                             │
                    Context Compression
                             │
                             ▼
                    Structured JSON
                             │
                             ▼
                 SHARED PATIENT DATABASE
                             │
                     Longitudinal History
                             │
                             ▼
                        DOCTOR SIDE
                             │
                       Doctor AI
                             │
               ┌─────────────┼──────────────┐
               │             │              │
         Past Context   Current Patient   Doctor/Test
                          Information      Findings
               │             │              │
               └─────────────┴──────────────┘
                             │
                             ▼
                  AI-Assisted Discussion
                             │
                             ▼
                           DOCTOR
                             │
                             ▼
                     FINAL DECISION
```

---

# 19. V1 Components to Build

The 20-day prototype contains the following major components:

### Patient Side

* Patient profile/account
* Nutrition AI
* Mental Wellness AI
* Conversation interface

### Context Processing

* CCEE
* clinical relevance extraction
* context compression
* redundancy reduction
* JSON generation

### Data Layer

* shared MongoDB database
* patient-based context storage
* source tracking
* timestamp/history support
* context retrieval

### Doctor Side

* Doctor account/interface
* Patient search
* Patient context retrieval
* Historical context display
* Doctor AI assistant
* Current consultation input
* Doctor-confirmed information storage

### Integration

* End-to-end communication
* Error handling
* Basic security controls
* Controlled test scenarios

---

# 20. Explicitly Out of Scope for V1

The following features MUST NOT be added during the initial 20-day development unless the project scope is intentionally revised later:

* autonomous disease diagnosis,
* universal disease prediction model,
* XGBoost disease prediction,
* SHAP disease prediction explanation,
* wearable-device integration,
* hospital EHR integration,
* FHIR integration,
* appointment booking,
* video consultation,
* pharmacy integration,
* payment systems,
* mobile application,
* calorie tracking application,
* advanced nutrition recommendation system,
* mental disorder diagnosis,
* hospital management features,
* microservice architecture,
* cloud-scale infrastructure,
* unnecessary vector databases,
* unnecessary multi-agent systems.

These may be explored as **future work**.

---

# 21. Research Focus

The main research question is not:

> "Can we create another healthcare chatbot?"

The research focus is:

> **How can clinically meaningful longitudinal patient context be extracted from specialized health conversations, compressed into a minimal structured representation, securely preserved, and later provided to doctors as contextual decision support?**

---

# 22. Main Research Contribution

The proposed framework combines:

1. Specialized Nutrition and Mental Wellness conversational systems.
2. Clinical Context Extraction Engine.
3. Minimal structured clinical-context storage.
4. Shared longitudinal patient context.
5. Doctor-side contextual retrieval and AI assistance.
6. Human-in-the-loop clinical decision making.

The contribution should not be claimed as a completely new AI algorithm unless future experimentation proves such novelty.

---

# 23. Primary Prototype Success Scenario

The V1 system will be considered functionally successful when the following complete scenario works:

```text
Patient creates account

↓

Patient talks to Nutrition AI

↓

CCEE extracts useful context

↓

Compact JSON stored

↓

Patient later talks to Mental Wellness AI

↓

CCEE extracts additional context

↓

Information is stored under SAME patient

↓

History develops over time

↓

Doctor selects patient

↓

Doctor AI retrieves relevant historical context

↓

Doctor enters current consultation information

↓

AI assists doctor using available context

↓

Doctor reviews information

↓

Doctor makes final decision
```

---

# 24. Development Principle

Both project members must understand and work on the complete system.

There will be no permanent separation such as:

```text
Member 1 = AI
Member 2 = Database
```

Both members will:

* learn the concepts,
* design the modules,
* review generated code,
* test the modules,
* understand the database,
* understand CCEE,
* understand the doctor workflow,
* understand the complete architecture.

AI coding assistants such as Antigravity may accelerate development, but architectural and research decisions remain with the project members.

---

# 25. 20-Day Scope

### Days 1–3

Patient-side architecture and Nutrition/Mental Wellness AI.

### Days 4–8

CCEE development and evaluation.

### Days 9–11

Shared MongoDB and longitudinal context storage.

### Days 12–15

Doctor-side AI and consultation workflow.

### Days 16–17

End-to-end integration.

### Days 18–19

Testing, debugging and evaluation.

### Day 20

Final prototype freeze, documentation, screenshots and research evidence.

---

# 26. Scope Change Rule

Any new feature suggested during development must answer:

1. Does it directly contribute to our core research problem?
2. Is it required for the V1 end-to-end flow?
3. Can it realistically be completed within 20 days?
4. Does it increase research value enough to justify the complexity?

If the answer is **no**, the feature goes to:

**FUTURE WORK**

and is not added to V1.

---

# 27. Final Project Principle

> **PCIF is not designed to replace medical professionals. It is designed to preserve meaningful longitudinal patient context and make that context available to clinicians when it can support better-informed medical decisions.**

The system should prioritize:

**Useful context over more data.**

**Structured information over conversation storage.**

**Longitudinal understanding over isolated interactions.**

**Clinical assistance over autonomous diagnosis.**

**Doctor authority over AI authority.**

---

## STATUS

**PCIF V1 SCOPE: FROZEN**

Changes should only be made when both team members intentionally agree that the research architecture itself needs revision.
