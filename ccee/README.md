# Clinical Context Extraction Engine (CCEE)

## Purpose
The CCEE module extracts, deduplicates, and compresses patient conversation histories into minimal, structured clinical JSON records.

## Data Pipeline
1. **Relevance Filter**: Discards conversational filler and non-health remarks.
2. **Redundancy Reduction**: Aggregates repeated logs into longitudinal trends.
3. **Context Compression**: Converts conversational sentences into brief clinical summaries.
4. **Structured Format**: Produces standard JSON entries matching `docs/CCEE_SCHEMA.md`.

## Development Schedule
- **Days 1–3**: Architecture and placeholder module.
- **Days 4–8**: Full CCEE engine development and evaluation.
