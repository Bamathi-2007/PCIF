# PCIF – Patient Context Intelligence Framework

## Purpose
**PCIF (Patient Context Intelligence Framework)** is a 20-day healthcare AI research prototype designed to extract, compress, and preserve clinically meaningful longitudinal patient context from specialized lifestyle and wellness conversations (Nutrition AI and Mental Wellness AI), presenting doctors with actionable decision support during patient consultations. The final clinical decision always belongs to the doctor.

---

## Core Architecture
The system follows a streamlined clinical context flow:

`Patient Conversations (Nutrition AI / Mental Wellness AI)`  
`→ Clinical Context Extraction Engine (CCEE)`  
`→ Minimal Structured Clinical JSON`  
`→ Shared MongoDB Patient Database`  
`→ Doctor Interface (Longitudinal Context Retrieval + AI Decision Support)`  
`→ Final Clinical Decision by Doctor`

---

## Current Development Status
- **Phase**: Day 1 - Repository Setup & Architecture Skeleton
- **Completed**: Clean modular folder structure, backend FastAPI route placeholders, CCEE engine stub, database schema placeholder, React Vite frontend UI skeleton, environment configuration, and foundational architecture documentation.
- **Pending (Intentionally NOT implemented today)**: AI conversation logic, CCEE extraction algorithms, active MongoDB connections, and Doctor AI assistant logic.

---

## Setup & Running Instructions

### Backend (Python FastAPI)
1. Ensure Python 3.10+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```
4. Run the backend server:
   ```bash
   python -m uvicorn backend.main:app --reload
   ```
5. View interactive API documentation at: `http://localhost:8000/docs`

### Frontend (React + Vite)
1. Ensure Node.js (v18+) is installed.
2. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Open the browser at the URL shown in terminal (e.g., `http://localhost:5173`).

---

## Project Structure

```text
PCIF/
├── backend/                  # FastAPI Python backend application
│   ├── app/
│   │   ├── api/              # API route modules (patient, nutrition, mental_wellness, ccee, doctor)
│   │   └── core/             # Configuration & environment management
│   ├── __init__.py
│   └── main.py               # Main application entrypoint
├── ccee/                     # Clinical Context Extraction Engine module
│   ├── engine.py             # CCEE extraction pipeline stub
│   ├── schema.py             # Structured JSON context schema stub
│   └── README.md             # CCEE principles & design rules
├── database/                 # Database integration module
│   ├── mongodb.py            # MongoDB connection stub & collections definition
│   └── README.md             # Database architecture documentation
├── docs/                     # Project documentation
│   ├── PROJECT_SCOPE_FREEZE.md   # Authoritative scope freeze document
│   ├── CCEE_SCHEMA.md            # Structured context schema definition
│   ├── TEST_CASES.md             # Test cases & scenario specifications
│   └── ARCHITECTURE.md           # System data flow diagram & documentation
├── frontend/                 # React + Vite frontend application
│   ├── src/
│   │   ├── components/       # Patient & Doctor dashboard components
│   │   ├── App.jsx           # Tab-based navigation router
│   │   ├── index.css         # Modern vanilla CSS design system
│   │   └── main.jsx          # React app entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .env.example              # Environment variables template
├── .gitignore                # Source control ignore rules
├── requirements.txt          # Python dependencies specification
└── README.md                 # Project overview and guide
```

---

## Authoritative Scope Reference
For complete scope rules, boundaries, and non-goals, refer to:
`docs/PROJECT_SCOPE_FREEZE.md`
