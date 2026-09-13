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

## 3. CCEE Synthetic Test Cases (Day 4 - Frozen V1 Contract)

The following 5 synthetic examples validate the frozen CCEE input/output contract, demonstrating context compression and relevance filtering without exhaustive entity extraction.

---

### Test Case 3.1: Skipped breakfast due early classes
- **Conversation**:
  - *User*: "I keep having to skip breakfast almost every morning because my college lectures start at 7:30 AM and I have to rush out."
- **Source**: `nutrition`
- **Expected Compact JSON**:
  ```json
  {
    "category": "nutrition",
    "summary": "Skipping breakfast regularly due to early morning class schedule",
    "source": "nutrition",
    "record_type": "patient_reported"
  }
  ```
- **Notes**: Captures the recurring meal skipping phenomenon and cause in one compressed record without creating separate fragmented fields for morning, college, or time.

---

### Test Case 3.2: Reduced sleep due exam stress
- **Conversation**:
  - *User*: "I've been sleeping around five hours because I'm stressed about exams for the last week."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
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
- **Notes**: Preserves specific quantitative duration and timeframe while combining stress trigger and sleep reduction into a single context item.

---

### Test Case 3.3: Reduced appetite for one week
- **Conversation**:
  - *User*: "For the past week, my appetite has dropped significantly and I feel full after eating barely half a meal."
- **Source**: `nutrition`
- **Expected Compact JSON**:
  ```json
  {
    "category": "appetite",
    "summary": "Marked reduction in appetite with early satiety",
    "value": "half a meal",
    "duration": "1 week",
    "source": "nutrition",
    "record_type": "patient_reported"
  }
  ```
- **Notes**: Retains the 1-week duration and quantitative measure without diagnosing an eating disorder.

---

### Test Case 3.4: Low water intake
- **Conversation**:
  - *User*: "I barely drink any water during the day, usually just one small glass because I get busy and keep forgetting."
- **Source**: `nutrition`
- **Expected Compact JSON**:
  ```json
  {
    "category": "hydration",
    "summary": "Low daily water intake due to forgetting during daily routine",
    "value": "1 glass/day",
    "source": "nutrition",
    "record_type": "patient_reported"
  }
  ```
- **Notes**: Preserves the qualitative/quantitative intake level without unnecessary key-value bloat.

---

### Test Case 3.5: Irrelevant conversation that should produce no context
- **Conversation**:
  - *User*: "Do you think it's going to rain this afternoon? I'm trying to decide if I should wash my car today or wait until the weekend."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  []
  ```
- **Notes**: Pure casual conversation with no clinical or lifestyle wellness relevance. Must yield an empty context list (`[]`).

---

## 4. CCEE Day 5 Synthetic Edge Cases (Relevance Filtering & Boundaries)

The following 5 synthetic edge cases validate clinical relevance filtering, minimum-sufficient context across multiple phenomena, diagnosis prevention, and uncertainty preservation.

---

### Test Case 4.1 (Edge Case A): Casual greeting
- **Conversation**:
  - *User*: "Hi, how are you today?"
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  []
  ```
- **Notes**: Casual conversational greeting with zero clinical or lifestyle relevance. Must yield an empty context list (`[]`).

---

### Test Case 4.2 (Edge Case B): Preference without health relevance
- **Conversation**:
  - *User*: "My favourite colour is yellow."
- **Source**: `nutrition`
- **Expected Compact JSON**:
  ```json
  []
  ```
- **Notes**: Personal preference with no dietary, nutritional, or clinical significance. Must yield an empty context list (`[]`).

---

### Test Case 4.3 (Edge Case C): Multiple meaningful phenomena
- **Conversation**:
  - *User*: "I've been skipping meals this week and sleeping only four hours because I'm stressed about exams."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "nutrition",
      "summary": "Skipping meals",
      "duration": "1 week",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    },
    {
      "category": "sleep",
      "summary": "Reduced sleep associated with exam stress",
      "value": "4 hours/night",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Recognizes genuinely distinct health phenomena (meal skipping and reduced sleep with exam stress) while avoiding entity explosion.

---

### Test Case 4.4 (Edge Case D): Unsupported diagnosis prevention
- **Conversation**:
  - *User*: "I've been feeling tired and sleeping only four hours."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "sleep",
      "summary": "Reduced sleep with reported tiredness",
      "value": "4 hours/night",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Represents only patient-reported phenomena. Must NOT infer clinical diagnoses such as "insomnia", "depression", or "chronic fatigue syndrome".

---

### Test Case 4.5 (Edge Case E): Uncertain self-report
- **Conversation**:
  - *User*: "I think I've been eating less than usual recently."
- **Source**: `nutrition`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "appetite",
      "summary": "Patient reports eating less than usual",
      "source": "nutrition",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Retains cautious/tentative language without inventing severity, exact quantities, or durations.

---

## 5. Doctor Retrieval Scenarios

### Scenario 5.1: Longitudinal Context Retrieval
- **Patient Context State**: Context records from both Nutrition AI and Mental Wellness AI over a 3-week period.
- **Doctor Query**: "Retrieve sleep and diet changes over the past month for Patient PAT-89210."
- **Expected Output**: Chronologically grouped context summarizing stress-sleep-appetite correlation.
- **Notes / Manual Test Log**: *(Space reserved for test execution logs)*

---

### Scenario 5.2: Doctor Consultation Entry & Decision Support
- **Doctor Consultation Input**: "Patient presents with persistent fatigue and mild epigastric discomfort."
- **Doctor AI Response**: Synthesizes patient-reported breakfast skipping and exam stress with clinician findings, providing context without autonomous diagnosis.
- **Notes / Manual Test Log**: *(Space reserved for test execution logs)*

