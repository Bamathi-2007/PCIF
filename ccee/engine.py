"""
Clinical Context Extraction Engine (CCEE) - Engine Implementation.

Processes patient conversations from Nutrition AI and Mental Wellness AI
and extracts minimal, structured, patient-reported clinical context items
conforming to the frozen CCEE schema.

Pipeline Flow:
Conversation Input (plain text or transcript turns) + Source AI
  ↓
1. Validation (Verify allowed source, normalize text input)
  ↓
2. Clinical Relevance Filtering (Rejects casual greetings, weather, non-health preferences)
  ↓
3. Context Compression & Redundancy Reduction (Synthesizes related causes/effects into single items)
  ↓
4. Structured Output Validation (Maps LLM JSON output to validated ClinicalContextItem objects)
  ↓
List[ClinicalContextItem]
"""

import logging
from typing import List, Dict, Any, Union, Optional
from ccee.schema import ClinicalContextItem, ALLOWED_SOURCES, ALLOWED_CATEGORIES
from backend.app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class ClinicalContextExtractionEngine:
    """
    Engine responsible for extracting structured, compressed clinical context
    from patient conversations.
    """

    def __init__(self, service=None):
        self._llm_service = service or llm_service

    def extract_context(
        self,
        conversation: Union[str, List[Dict[str, Any]]],
        source: str
    ) -> List[ClinicalContextItem]:
        """
        Extracts a list of validated ClinicalContextItem objects from conversation text.

        Args:
            conversation (Union[str, List[Dict[str, Any]]]): Conversational text or list of message turns.
            source (str): Source AI module ('nutrition' or 'mental_wellness').

        Returns:
            List[ClinicalContextItem]: Extracted, validated clinical context items, or [] if no clinical context exists.

        Raises:
            ValueError: If source is invalid or not in ALLOWED_SOURCES.
        """
        if not source or source not in ALLOWED_SOURCES:
            raise ValueError(
                f"Invalid source '{source}'. Allowed sources: {ALLOWED_SOURCES}"
            )

        # Normalize conversation input to plain text
        conversation_text = self._normalize_conversation(conversation)
        if not conversation_text.strip():
            return []

        # Call shared LLM service for structured extraction
        try:
            raw_items = self._llm_service.extract_ccee(
                conversation_text=conversation_text,
                source=source
            )
        except Exception as e:
            logger.error(f"CCEE extraction error: {e}", exc_info=True)
            # Re-raise rate limits so caller/evaluator is aware
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "503" in error_str or "UNAVAILABLE" in error_str:
                raise
            # Return empty list for other controlled extraction failures
            return []

        if not raw_items:
            return []

        # Validate and convert raw items to ClinicalContextItem instances
        validated_items: List[ClinicalContextItem] = []
        for raw in raw_items:
            try:
                # Ensure source is strictly mapped to the current source
                raw["source"] = source
                item = ClinicalContextItem.from_dict(raw)
                validated_items.append(item)
            except (ValueError, TypeError, KeyError) as ve:
                logger.warning(f"Discarding invalid context item {raw}: {ve}")
                continue

        # Minimal deterministic safeguard: eliminate duplicate extractions of identical category and summary
        return self._deduplicate_items(validated_items)

    @staticmethod
    def _deduplicate_items(items: List[ClinicalContextItem]) -> List[ClinicalContextItem]:
        """
        Minimal deterministic post-validation safeguard: removes exact or near-identical
        duplicate items sharing the same category and normalized summary within the current extraction.
        Preserves richer value/duration if present.
        """
        unique_items: List[ClinicalContextItem] = []
        seen_keys = set()

        for item in items:
            key = (item.category, item.summary.strip().lower())
            if key not in seen_keys:
                seen_keys.add(key)
                unique_items.append(item)
            else:
                # If seen, merge value or duration into existing item if missing
                existing = next(i for i in unique_items if (i.category, i.summary.strip().lower()) == key)
                if not existing.value and item.value:
                    existing.value = item.value
                if not existing.duration and item.duration:
                    existing.duration = item.duration

        return unique_items

    @staticmethod
    def _normalize_conversation(conversation: Union[str, List[Dict[str, Any]]]) -> str:
        """Converts text or message turn dictionaries into normalized conversation text."""
        if isinstance(conversation, str):
            return conversation.strip()

        if isinstance(conversation, list):
            lines = []
            for turn in conversation:
                if isinstance(turn, dict):
                    role = turn.get("role", "User").capitalize()
                    content = turn.get("content", "").strip()
                    if content:
                        lines.append(f"{role}: {content}")
                elif isinstance(turn, str) and turn.strip():
                    lines.append(turn.strip())
            return "\n".join(lines)

        return ""


ccee_engine = ClinicalContextExtractionEngine()
