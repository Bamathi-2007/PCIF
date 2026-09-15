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

## 5. CCEE Day 6 Synthetic Test Cases (Redundancy Reduction & Context Compression)

The following 7 synthetic test cases validate CCEE's semantic compression and redundancy reduction within a single conversation session. The goal is to store the minimum-sufficient context items needed to preserve clinically useful meaning while avoiding unnecessary entity splitting or duplicate records.

---

### Test Case 5.1 (Day 6 Case 1): Exact / repeated sleep meaning
- **Conversation**:
  - *User*: "I've been sleeping only five hours lately. Most nights I get about five hours because I'm studying late. My sleep has definitely reduced."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "sleep",
      "summary": "Reduced sleep associated with late-night studying",
      "value": "approximately 5 hours/night",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Multiple restatements of 5-hour sleep and late study consolidate into exactly ONE sleep item preserving ~5 hours/night.

---

### Test Case 5.2 (Day 6 Case 2): Stress as context, not independent record
- **Conversation**:
  - *User*: "I'm stressed about my exams and because of that I'm sleeping only four hours every night."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "sleep",
      "summary": "Reduced sleep associated with exam stress",
      "value": "4 hours/night",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Exam stress is folded into the sleep record as situational context/cause. Does NOT create an unnecessary separate stress record.

---

### Test Case 5.3 (Day 6 Case 3): Two genuinely distinct phenomena & Temporal Attachment
- **Conversation**:
  - *User*: "I'm sleeping only four hours and I've also lost my appetite this week."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "sleep",
      "summary": "Reduced sleep",
      "value": "4 hours/night",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    },
    {
      "category": "appetite",
      "summary": "Reduced appetite",
      "duration": "1 week",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Keeps distinct health phenomena (sleep impairment and appetite loss) cleanly separate. Attaches duration "1 week" strictly to appetite (the phenomenon it clearly describes) and does NOT propagate it to sleep.

---

### Test Case 5.4 (Day 6 Case 4): Repeated nutrition meaning
- **Conversation**:
  - *User*: "I keep skipping breakfast. I usually don't eat anything in the morning before college. Most weekdays I leave without breakfast because my first class is early."
- **Source**: `nutrition`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "nutrition",
      "summary": "Regularly skipping breakfast due to early college class schedule",
      "source": "nutrition",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Consolidates three near-duplicate statements about skipping breakfast into ONE compressed nutrition item.

---

### Test Case 5.5 (Day 6 Case 5): Related hydration repetition & Uncertainty Preservation
- **Conversation**:
  - *User*: "I forget to drink water at college. Some days I only drink one glass. I stay busy and hardly drink water until evening."
- **Source**: `nutrition`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "hydration",
      "summary": "Low water intake due to forgetting during busy college routine",
      "value": "1 glass on some days",
      "source": "nutrition",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Merges repetitive low water intake remarks into ONE hydration record; preserves the episodic qualifier "on some days" without converting it into an absolute daily frequency (e.g. does NOT output "1 glass/day").

---

### Test Case 5.6 (Day 6 Case 6): Independent stress should remain
- **Conversation**:
  - *User*: "I feel overwhelmed throughout the entire day because of exams. I can't concentrate on normal tasks. I'm also sleeping around four hours at night."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "stress",
      "summary": "Persistent daytime overwhelm and impaired concentration associated with exams",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    },
    {
      "category": "sleep",
      "summary": "Reduced sleep",
      "value": "approximately 4 hours/night",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Stress has independent daytime functional impact (inability to concentrate), so retaining TWO records (stress and sleep) is clinically justified.

---

### Test Case 5.7 (Day 6 Case 7): Irrelevant repetition
- **Conversation**:
  - *User*: "Hi. Hello again. By the way my favourite colour is yellow. I really like yellow."
- **Source**: `nutrition`
- **Expected Compact JSON**:
  ```json
  []
  ```
- **Notes**: Repetitive greetings and non-health preferences remain completely filtered out, returning an empty list `[]`.

---

---

## 6. CCEE Day 7 Synthetic Test Cases (Temporal Context, Supersession & Source Integrity)

The following 9 synthetic test cases validate CCEE's understanding of temporal context, explicit in-conversation self-corrections, past vs. current state transitions, ongoing durations, resolved past events, assistant-turn safety, and strict source integrity within a single conversation session.

---

### Test Case 6.1 (Day 7 Case 1): Explicit self-correction
- **Conversation**:
  - *User*: "I've been sleeping around three hours. Actually, I think it's closer to five hours."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "sleep",
      "summary": "Reduced sleep duration",
      "value": "approximately 5 hours/night",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: The explicit self-correction ("closer to five hours") supersedes the earlier statement ("three hours"). The superseded 3-hour metric is NOT retained as an active second record.

---

### Test Case 6.2 (Day 7 Case 2): Past → current improvement
- **Conversation**:
  - *User*: "Last week I was sleeping around four hours, but this week I'm back to about seven hours."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "sleep",
      "summary": "Sleep improved from approximately 4 hours/night last week to 7 hours/night currently",
      "value": "approximately 7 hours/night",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Captures the temporal shift into a single compressed item. Current `value` reflects current state (7 hours/night) and past state (4 hours/night) is preserved as historical context in `summary`.

---

### Test Case 6.3 (Day 7 Case 3): Ongoing duration
- **Conversation**:
  - *User*: "I've been sleeping around five hours every night for the past two weeks."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "sleep",
      "summary": "Reduced sleep duration",
      "value": "approximately 5 hours/night",
      "duration": "2 weeks",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Recognizes "for the past two weeks" as an ongoing duration and populates `duration` accordingly.

---

### Test Case 6.4 (Day 7 Case 4): Resolved insignificant past event
- **Conversation**:
  - *User*: "I had one night where I barely slept about three months ago, but my sleep has been normal ever since."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  []
  ```
- **Notes**: An isolated, completely resolved past event from 3 months ago with no ongoing clinical context yields an empty list `[]`.

---

### Test Case 6.5 (Day 7 Case 5): Ongoing worsening appetite & Approximate Duration
- **Conversation**:
  - *User*: "My appetite started decreasing about two weeks ago, and it still seems to be getting worse."
- **Source**: `nutrition`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "appetite",
      "summary": "Decreased appetite for approximately two weeks with reported ongoing worsening",
      "duration": "approximately 2 weeks",
      "source": "nutrition",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Captures the duration while preserving the approximate qualifier ("about two weeks" -> "approximately 2 weeks"). Does NOT strip the approximate qualifier.

---

### Test Case 6.6 (Day 7 Case 6): Temporal decline
- **Conversation**:
  - *User*: "Earlier this month I was sleeping around six hours. This week it's down to four hours because assignments are keeping me up."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "sleep",
      "summary": "Sleep decreased from approximately 6 hours/night earlier this month to 4 hours/night this week, associated with assignment workload",
      "value": "4 hours/night",
      "duration": "this week",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Synthesizes the sleep decline (from 6h to 4h) into ONE record with current value `4 hours/night` and assignment context.

---

### Test Case 6.7 (Day 7 Case 7): Distinct temporal phenomena
- **Conversation**:
  - *User*: "My sleep has improved this week, but my appetite has been getting worse for about two weeks."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "sleep",
      "summary": "Reported improvement in sleep",
      "duration": "this week",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    },
    {
      "category": "appetite",
      "summary": "Worsening appetite over recent weeks",
      "duration": "approximately 2 weeks",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Distinct phenomena (sleep improvement vs. appetite worsening) remain 2 separate records despite different temporal trajectories.

---

### Test Case 6.8 (Day 7 Case 8): Source integrity
- **Conversation**:
  - *User*: "I've been sleeping only five hours lately because my meal schedule keeps me up late."
- **Source**: `nutrition`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "sleep",
      "summary": "Reduced sleep associated with late meal schedule",
      "value": "5 hours/night",
      "source": "nutrition",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Even though category is `sleep`, the `source` field MUST strictly remain `nutrition` because the conversation originated from Nutrition AI.

---

### Test Case 6.9 (Day 7 Case 9): Multi-turn transcript & Calendar-Relative Duration
- **Conversation (Transcript Turns)**:
  - *User*: "I'm sleeping only three hours."
  - *Assistant*: "Has that been happening every night?"
  - *User*: "Actually I exaggerated — it's closer to five hours, mostly this week."
- **Source**: `mental_wellness`
- **Expected Compact JSON**:
  ```json
  [
    {
      "category": "sleep",
      "summary": "Reduced sleep duration",
      "value": "approximately 5 hours/night",
      "duration": "this week",
      "source": "mental_wellness",
      "record_type": "patient_reported"
    }
  ]
  ```
- **Notes**: Demonstrates multi-turn handling. User's self-correction ("closer to five hours, mostly this week") is extracted as current truth; calendar-relative duration "this week" is preserved as "this week" and NOT converted to "1 week". Assistant questions are context, NOT patient facts.

---

## 7. Doctor Retrieval Scenarios

### Scenario 7.1: Longitudinal Context Retrieval
- **Patient Context State**: Context records from both Nutrition AI and Mental Wellness AI over a 3-week period.
- **Doctor Query**: "Retrieve sleep and diet changes over the past month for Patient PAT-89210."
- **Expected Output**: Chronologically grouped context summarizing stress-sleep-appetite correlation.
- **Notes / Manual Test Log**: *(Space reserved for test execution logs)*

---

### Scenario 7.2: Doctor Consultation Entry & Decision Support
- **Doctor Consultation Input**: "Patient presents with persistent fatigue and mild epigastric discomfort."
- **Doctor AI Response**: Synthesizes patient-reported breakfast skipping and exam stress with clinician findings, providing context without autonomous diagnosis.
- **Notes / Manual Test Log**: *(Space reserved for test execution logs)*

