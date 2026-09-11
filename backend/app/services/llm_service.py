"""
PCIF LLM Service.
Provides a shared backend interface to Google Gemini using the google-genai SDK
and the stateless Gemini Interactions API (configured with store=False).
"""

import os
import logging
from typing import Optional, List, Dict
from dotenv import load_dotenv
from google import genai
from backend.app.core.config import settings
from backend.app.prompts import NUTRITION_SYSTEM_INSTRUCTION, MENTAL_WELLNESS_SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)


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


llm_service = GeminiLLMService()

