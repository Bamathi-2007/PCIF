# PCIF Architecture Overview

The **Patient Context Intelligence Framework (PCIF)** is designed to capture, compress, and present longitudinal patient context to support clinician decision-making.

---

## High-Level Data Flow

```mermaid
flowchart TD
    subgraph PatientSide["Patient-Facing System"]
        PA[Patient Account]
        NAI["Nutrition AI (Physical/Lifestyle)"]
        MAI["Mental Wellness AI (Mood/Sleep/Stress)"]
        PA --> NAI
        PA --> MAI
    end

    subgraph ContextProcessing["Clinical Context Extraction Engine (CCEE)"]
        RF[Relevance Filter]
        RR[Redundancy Reduction]
        CC[Context Compression]
        JSON[Compact Structured JSON]
        
        NAI --> CCEE
        MAI --> CCEE
        CCEE --> RF --> RR --> CC --> JSON
    end

    subgraph DataLayer["Shared Data Layer"]
        MDB[("Shared MongoDB Patient Database")]
        JSON --> MDB
    end

    subgraph DoctorSide["Doctor-Facing System"]
        DS[Doctor Interface]
        DAI[Doctor AI Assistant]
        MDB --> DS
        DS --> DAI
        CI[Current Consultation Input] --> DAI
        DAI --> Discussion[AI-Assisted Discussion]
        Discussion --> Doctor[Doctor Clinical Decision]
    end

    classDef patient fill:#2a3a5e,stroke:#4a6fa5,color:#fff;
    classDef ccee fill:#2e5a44,stroke:#3b8256,color:#fff;
    classDef db fill:#5a3e2e,stroke:#a56f4a,color:#fff;
    classDef doctor fill:#4a2e5a,stroke:#823b82,color:#fff;

    class PA,NAI,MAI patient;
    class RF,RR,CC,JSON ccee;
    class MDB db;
    class DS,DAI,CI,Discussion,Doctor doctor;
```

---

## Component Boundaries

### 1. Patient Interface (`frontend/` & `backend/app/api/`)
- Dual conversational AI interfaces: **Nutrition AI** and **Mental Wellness AI**.
- Both interfaces interact with the patient under the **same unified patient profile**.

### 2. Clinical Context Extraction Engine (`ccee/`)
- Receives conversational transcripts from patient AI sessions.
- Applies relevance filtering, deduplication, and compression.
- Formats structured clinical items for database persistence.

### 3. Data Layer (`database/`)
- Single shared database repository (MongoDB).
- Preserves explicit source lineage (`nutrition`, `mental_wellness`, `doctor`).
- Supports longitudinal history querying by patient ID.

### 4. Doctor System (`backend/app/api/doctor.py` & Doctor Dashboard)
- Enables searching patient records, retrieving longitudinal context timelines.
- Integrates clinician-entered consultation notes with patient-reported context.
- Doctor AI serves purely as contextual decision support (human-in-the-loop).
