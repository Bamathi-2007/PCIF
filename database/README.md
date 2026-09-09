# Shared MongoDB Patient Database

## Logical Collections
1. **`users`**: Patient and Doctor profiles.
2. **`patient_context`**: Extracted structured clinical context items from CCEE and doctor observations.
3. **`doctor_notes`**: Consultation records and clinician findings.

## Source Tracking Principle
Every record in `patient_context` maintains explicit `source` attribution (`nutrition`, `mental_wellness`, or `doctor`) to distinguish patient-reported context from clinician-confirmed diagnosis.

## Integration Schedule
MongoDB integration is scheduled for Days 9–11.
