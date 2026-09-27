"""
PCIF LLM Service.
Provides a shared backend interface to Google Gemini using the google-genai SDK
and the stateless Gemini Interactions API (configured with store=False).
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types
from backend.app.core.config import settings
from backend.app.prompts import (
    NUTRITION_SYSTEM_INSTRUCTION,
    MENTAL_WELLNESS_SYSTEM_INSTRUCTION,
    CCEE_SYSTEM_INSTRUCTION,
    LONGITUDINAL_RELATION_SYSTEM_INSTRUCTION,
    DOCTOR_CONTEXT_SYSTEM_INSTRUCTION,
)
from ccee.schema import CCEEExtractionResult

logger = logging.getLogger(__name__)


class LongitudinalRelationResult(BaseModel):
    relation: Literal["duplicate", "update", "distinct"] = Field(
        description="Relationship classification: 'duplicate', 'update', or 'distinct'."
    )


class DoctorContextResponseSchema(BaseModel):
    context_summary: str = Field(
        default="",
        description="Concise background summary synthesizing relevant context across provenance sources with current consultation."
    )
    relevant_current_context: List[str] = Field(
        default_factory=list,
        description="List of relevant active current patient-reported context statements."
    )
    relevant_longitudinal_changes: List[str] = Field(
        default_factory=list,
        description="List of relevant longitudinal shifts or trend observations over stored patient-reported history."
    )
    relevant_clinician_notes: List[str] = Field(
        default_factory=list,
        description="List of relevant historical clinician-authored notes or findings relevant to this consultation."
    )
    items_to_verify: List[str] = Field(
        default_factory=list,
        description="List of discrepancies between sources, items needing clinician verification, or important follow-ups."
    )



class GeminiLLMService:
    """Reusable LLM service for communicating statelessly with Google Gemini."""

    def __init__(self):
        self._client: Optional[genai.Client] = None
        self._cached_api_key: Optional[str] = None

    def _get_client(self) -> Optional[genai.Client]:
        """Lazy-initialize and return the Gemini client if API key is present."""
        load_dotenv(override=True)
        api_key = os.getenv("GEMINI_API_KEY", settings.GEMINI_API_KEY).strip()
        if not api_key:
            return None
        # Re-instantiate if key changed or not yet created
        if self._client is None or self._cached_api_key != api_key:
            self._cached_api_key = api_key
            self._client = genai.Client(api_key=api_key)
        return self._client

    def _chat(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]],
        system_instruction: str,
        service_name: str
    ) -> str:
        """
        Shared stateless interaction method calling Google Gemini via the Interactions API.
        
        Preserves:
        - Gemini Interactions persistence is disabled using store=False, and PCIF does not persist raw conversations in its own database during the current prototype.
        - no previous_interaction_id
        - sanitized in-memory conversation steps
        - graceful error handling
        """
        client = self._get_client()
        if client is None:
            return (
                f"[{service_name} Notice] GEMINI_API_KEY is not configured in backend .env. "
                "Please configure your Gemini API key in .env to enable live conversational responses."
            )

        model_name = os.getenv("GEMINI_MODEL", settings.GEMINI_MODEL) or "gemini-3.8-flash"

        # Safely construct stateless input steps from validated turns
        steps: List[Dict] = []

        if history:
            for turn in history:
                role = turn.get("role", "").strip().lower()
                text = turn.get("content", "").strip()
                if not text:
                    continue

                # Safely map only recognized conversational roles; reject system instructions
                if role == "user":
                    steps.append({
                        "type": "user_input",
                        "content": [{"type": "text", "text": text}]
                    })
                elif role == "assistant":
                    steps.append({
                        "type": "model_output",
                        "content": [{"type": "text", "text": text}]
                    })

        # Append current user message
        steps.append({
            "type": "user_input",
            "content": [{"type": "text", "text": message.strip()}]
        })

        try:
            # Call Interactions API with store=False for stateless operation
            interaction = client.interactions.create(
                model=model_name,
                input=steps,
                system_instruction=system_instruction,
                store=False,
            )

            # Retrieve generated text response
            reply_text = getattr(interaction, "output_text", None) or ""
            return reply_text

        except Exception as e:
            logger.error(f"Error calling Gemini Interactions API for {service_name}: {e}", exc_info=True)
            error_str = str(e)

            # User-friendly guidance for common configuration issues
            if "API_KEY_INVALID" in error_str or "401" in error_str or "API key not valid" in error_str:
                return (
                    "Authentication error: The provided GEMINI_API_KEY is invalid. "
                    "Please verify your API key in .env."
                )
            elif "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                return (
                    "The Gemini API rate limit has been reached. Please wait a moment and try again."
                )

            return (
                f"I'm having trouble connecting to the {service_name.lower()} right now. Please try again shortly."
            )

    def chat_nutrition(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Sends a user message and temporary in-memory history to the Nutrition AI
        via the Gemini Interactions API in stateless mode (store=False).
        """
        return self._chat(
            message=message,
            history=history,
            system_instruction=NUTRITION_SYSTEM_INSTRUCTION,
            service_name="Nutrition AI"
        )

    def chat_mental_wellness(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Sends a user message and temporary in-memory history to the Mental Wellness AI
        via the Gemini Interactions API in stateless mode (store=False).
        """
        return self._chat(
            message=message,
            history=history,
            system_instruction=MENTAL_WELLNESS_SYSTEM_INSTRUCTION,
            service_name="Mental Wellness AI"
        )

    def extract_ccee(
        self,
        conversation_text: str,
        source: str
    ) -> List[Dict[str, Any]]:
        """
        Extracts structured clinical context items from conversation text using Google Gemini
        with structured JSON output validated against the frozen CCEE schema.

        Returns a list of raw extracted dictionaries, or empty list if no clinical context is found.
        """
        client = self._get_client()
        if client is None:
            logger.warning("Gemini client unavailable: GEMINI_API_KEY is not configured.")
            raise RuntimeError("Gemini client unavailable: GEMINI_API_KEY is not configured in backend environment.")


        model_name = os.getenv("GEMINI_MODEL", settings.GEMINI_MODEL) or "gemini-3.8-flash"

        prompt = (
            f"SOURCE AGENT: {source}\n\n"
            f"PATIENT CONVERSATION TRANSCRIPT:\n\"\"\"\n{conversation_text.strip()}\n\"\"\"\n\n"
            "Analyze the above conversation according to your instructions. "
            "Extract only clinically or contextually useful patient-reported health/lifestyle information. "
            "If the conversation is purely casual greetings, weather, non-health preferences, or irrelevant, return items: []."
        )

        try:
            config = types.GenerateContentConfig(
                system_instruction=CCEE_SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=CCEEExtractionResult,
                temperature=0.0,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )

            raw_text = response.text or "{}"
            data = json.loads(raw_text)

            if not isinstance(data, dict) or "items" not in data or not isinstance(data.get("items"), list):
                logger.error(f"Malformed CCEE response structure: {raw_text}")
                raise RuntimeError(f"CCEE extraction failed: Malformed top-level JSON response structure: {raw_text}")

            raw_items = data["items"]

            cleaned_items: List[Dict[str, Any]] = []
            for item in raw_items:
                if isinstance(item, dict):
                    # Guarantee source and default record_type
                    item["source"] = source
                    if "record_type" not in item or not item["record_type"]:
                        item["record_type"] = "patient_reported"
                    cleaned_items.append(item)

            return cleaned_items

        except Exception as e:
            error_str = str(e)
            logger.error(f"Error extracting CCEE context via Gemini: {error_str}", exc_info=True)
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                raise RuntimeError(f"Gemini API rate limit reached (429): {error_str}") from e
            # Controlled failure for other errors: log and re-raise or return empty list
            raise RuntimeError(f"CCEE extraction failed: {error_str}") from e

    def classify_longitudinal_relation(
        self,
        existing_item: Dict[str, Any],
        new_item: Dict[str, Any]
    ) -> str:
        """
        Classifies the relationship between an existing active context record
        and a newly extracted context item for the same patient.

        Returns one of: 'duplicate', 'update', or 'distinct'.
        Defaults to 'distinct' on any error, timeout, or missing Gemini client.
        """
        client = self._get_client()
        if client is None:
            logger.warning("Gemini client unavailable for longitudinal classification; defaulting to 'distinct'.")
            return "distinct"

        model_name = os.getenv("GEMINI_MODEL", settings.GEMINI_MODEL) or "gemini-3.8-flash"

        # Sanitize items for structured prompt (exclude database metadata fields)
        clean_existing = {
            "category": existing_item.get("category"),
            "summary": existing_item.get("summary"),
            "value": existing_item.get("value"),
            "duration": existing_item.get("duration"),
            "source": existing_item.get("source"),
        }
        clean_new = {
            "category": new_item.get("category"),
            "summary": new_item.get("summary"),
            "value": new_item.get("value"),
            "duration": new_item.get("duration"),
            "source": new_item.get("source"),
        }

        prompt = (
            "EXISTING STORED ITEM:\n"
            f"{json.dumps(clean_existing, indent=2)}\n\n"
            "NEW ITEM:\n"
            f"{json.dumps(clean_new, indent=2)}\n\n"
            "Analyze the above two structured context items and determine their relation."
        )

        try:
            config = types.GenerateContentConfig(
                system_instruction=LONGITUDINAL_RELATION_SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=LongitudinalRelationResult,
                temperature=0.0,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )

            raw_text = response.text or "{}"
            data = json.loads(raw_text)
            rel = data.get("relation", "").strip().lower()
            if rel in ("duplicate", "update", "distinct"):
                return rel

            logger.warning(f"Unexpected relation response '{rel}', defaulting to 'distinct'.")
            return "distinct"

        except Exception as e:
            logger.warning(f"Longitudinal relation classification error ({e}); defaulting safely to 'distinct'.")
            return "distinct"

    def generate_doctor_context_assistance(
        self,
        patient_id: str,
        consultation: str,
        current_context: List[Dict[str, Any]],
        longitudinal_history: List[Dict[str, Any]],
        clinician_notes: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generates doctor-facing contextual assistance synthesizing active current patient-reported profile,
        longitudinal patient-reported history, clinician-authored notes, and current consultation details.
        """
        client = self._get_client()
        if client is None:
            logger.warning("Gemini client unavailable for doctor context assistance.")
            return {
                "context_summary": "Notice: Gemini API key is not configured. Contextual assistance is unavailable.",
                "relevant_current_context": [],
                "relevant_longitudinal_changes": [],
                "relevant_clinician_notes": [],
                "items_to_verify": []
            }

        model_name = os.getenv("GEMINI_MODEL", settings.GEMINI_MODEL) or "gemini-3.8-flash"

        # Clean current profile items (exclude internal MongoDB metadata)
        clean_current = []
        for doc in current_context:
            clean_current.append({
                "category": doc.get("category"),
                "summary": doc.get("summary"),
                "source": doc.get("source"),
                "record_type": doc.get("record_type", "patient_reported"),
                "value": doc.get("value"),
                "duration": doc.get("duration"),
            })

        # Clean longitudinal history items
        clean_history = []
        for doc in longitudinal_history:
            captured_at_val = doc.get("captured_at")
            if isinstance(captured_at_val, datetime):
                captured_at_str = captured_at_val.isoformat()
            else:
                captured_at_str = str(captured_at_val) if captured_at_val else None

            clean_history.append({
                "category": doc.get("category"),
                "summary": doc.get("summary"),
                "source": doc.get("source"),
                "record_type": doc.get("record_type", "patient_reported"),
                "value": doc.get("value"),
                "duration": doc.get("duration"),
                "is_current": doc.get("is_current", True),
                "recorded_at": captured_at_str,
            })

        # Clean clinician-authored notes (exclude raw ObjectIds, internal fields)
        clean_clinician_notes = []
        if clinician_notes:
            for doc in clinician_notes:
                created_at_val = doc.get("created_at") or doc.get("saved_at")
                if isinstance(created_at_val, datetime):
                    saved_at_str = created_at_val.isoformat()
                else:
                    saved_at_str = str(created_at_val) if created_at_val else None

                clean_clinician_notes.append({
                    "note": doc.get("note", ""),
                    "provenance": "clinician_authored",
                    "saved_at": saved_at_str,
                })

        prompt = (
            f"PATIENT ID: {patient_id}\n\n"
            f"[SOURCE A: CURRENT CLINICIAN CONSULTATION NOTES]\n\"\"\"\n{consultation.strip()}\n\"\"\"\n\n"
            f"[SOURCE B: PATIENT-REPORTED CONTEXT]\n"
            f"Active Current Patient-Reported Profile:\n{json.dumps(clean_current, indent=2)}\n\n"
            f"Longitudinal Patient-Reported History:\n{json.dumps(clean_history, indent=2)}\n\n"
            f"[SOURCE C: CLINICIAN-AUTHORED HISTORICAL NOTES]\n"
            f"Clinician-Authored Notes History:\n{json.dumps(clean_clinician_notes, indent=2)}\n\n"
            "Analyze the above three sources according to your system instructions. "
            "Synthesize relevant background context with the consultation notes and return a structured DoctorContextResponse JSON."
        )

        try:
            config = types.GenerateContentConfig(
                system_instruction=DOCTOR_CONTEXT_SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=DoctorContextResponseSchema,
                temperature=0.0,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )

            raw_text = response.text or "{}"
            data = json.loads(raw_text)

            return {
                "context_summary": data.get("context_summary", ""),
                "relevant_current_context": data.get("relevant_current_context", []),
                "relevant_longitudinal_changes": data.get("relevant_longitudinal_changes", []),
                "relevant_clinician_notes": data.get("relevant_clinician_notes", []),
                "items_to_verify": data.get("items_to_verify", []),
            }

        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generating doctor context assistance: {error_str}", exc_info=True)
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                raise RuntimeError(f"Gemini API rate limit reached (429): {error_str}") from e
            raise RuntimeError(f"Doctor context assistance generation failed: {error_str}") from e


llm_service = GeminiLLMService()



