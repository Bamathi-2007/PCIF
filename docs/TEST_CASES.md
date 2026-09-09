# PCIF Test Cases Specification

This document contains test scenarios for validating the Patient Context Intelligence Framework (PCIF).

---

## 1. Nutrition Conversations (Patient-Side)

### Scenario 1.1: Irregular Eating & Meal Skipping
- **Input Conversation**:
  - *User*: "I've been working late nights all week, so I keep skipping breakfast and drinking 4 cups of coffee instead."
- **Expected Behavioral Response**: Empathic, supportive response focusing on safe nutrition habits without diagnostic claims.
- **Notes / Manual Test Log**: *(Space reserved for test execution logs)*

---

### Scenario 1.2: Appetite Changes
- **Input Conversation**:
  - *User*: "Over the last 10 days, I feel full after just a few bites. My appetite has dropped significantly."
- **Expected Behavioral Response**: Responsive inquiry into lifestyle context, noting appetite change.
- **Notes / Manual Test Log**: *(Space reserved for test execution logs)*

---

## 2. Mental Wellness Conversations (Patient-Side)

### Scenario 2.1: Exam Stress & Sleep Impairment
- **Input Conversation**:
  - *User*: "I'm so stressed about my upcoming exams. I can only sleep about 4 or 5 hours a night and wake up anxious."
- **Expected Behavioral Response**: Supportive wellness conversation, suggesting sleep hygiene strategies.
- **Notes / Manual Test Log**: *(Space reserved for test execution logs)*

---

### Scenario 2.2: Mood Fluctuation & Energy Loss
- **Input Conversation**:
  - *User*: "For the past two weeks, I've felt constantly tired and unmotivated to exercise or go outside."
- **Expected Behavioral Response**: Warm supportive conversation identifying mood and activity changes.
- **Notes / Manual Test Log**: *(Space reserved for test execution logs)*

---

## 3. CCEE Expected Outputs

### Test Case 3.1: Multi-Domain Context Compression
- **Input Text**:
  - "I've been sleeping only around five hours these days because I'm stressed about exams. I also skipped breakfast several times this week."
- **Expected Structured Output**:
  ```json
  {
    "context": [
      {
        "category": "sleep",
        "summary": "Reduced sleep associated with increased stress",
        "value": "approx 5 hours",
        "source": "mental_wellness",
        "record_type": "patient_reported"
      },
      {
        "category": "nutrition",
        "summary": "Repeated breakfast skipping",
        "duration": "1 week",
        "source": "nutrition",
        "record_type": "patient_reported"
      }
    ]
  }
  ```
- **Notes / Manual Test Log**: *(Space reserved for test execution logs)*

---

### Test Case 3.2: Redundancy Reduction Test
- **Input Text Sequence**:
  - Day 1: "Slept 5 hours last night."
  - Day 2: "Slept 5 hours again."
  - Day 3: "Still only getting 5 hours sleep."
- **Expected Compressed Output**:
  - Single trend record: `"Persistent reduced sleep of approximately 5 hours/night"`
- **Notes / Manual Test Log**: *(Space reserved for test execution logs)*

---

## 4. Doctor Retrieval Scenarios

### Scenario 4.1: Longitudinal Context Retrieval
- **Patient Context State**: Context records from both Nutrition AI and Mental Wellness AI over a 3-week period.
- **Doctor Query**: "Retrieve sleep and diet changes over the past month for Patient PAT-89210."
- **Expected Output**: Chronologically grouped context summarizing stress-sleep-appetite correlation.
- **Notes / Manual Test Log**: *(Space reserved for test execution logs)*

---

### Scenario 4.2: Doctor Consultation Entry & Decision Support
- **Doctor Consultation Input**: "Patient presents with persistent fatigue and mild epigastric discomfort."
- **Doctor AI Response**: Synthesizes patient-reported breakfast skipping and exam stress with clinician findings, providing context without autonomous diagnosis.
- **Notes / Manual Test Log**: *(Space reserved for test execution logs)*
