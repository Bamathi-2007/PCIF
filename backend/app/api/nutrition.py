"""
PCIF Nutrition AI API Routes.
Provides patient-facing conversational endpoints for nutrition and healthy-lifestyle guidance.
"""

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.app.services.llm_service import llm_service

router = APIRouter(prefix="/nutrition", tags=["Nutrition AI"])


class ChatTurn(BaseModel):
    role: str = Field(..., description="Role of the speaker: 'user' or 'assistant'")
    content: str = Field(..., description="Turn text content")


class NutritionChatRequest(BaseModel):
    message: str = Field(..., description="Current patient input message")
    history: List[ChatTurn] = Field(
        default_factory=list,
        description="Temporary in-memory conversation history for the active session"
    )


class NutritionChatResponse(BaseModel):
    source: str = "nutrition"
    reply: str
    status: str = "success"


@router.post("/chat", response_model=NutritionChatResponse)
async def nutrition_chat(payload: NutritionChatRequest):
    """
    Nutrition AI conversational chat endpoint.
    Statelessly processes multi-turn context sent by the client.
    Configured with Gemini store=false (no provider-side interaction persistence).
    Raw conversation history is not persisted in the PCIF application database during the prototype.
    """
    history_dicts = [{"role": turn.role, "content": turn.content} for turn in payload.history]

    reply = llm_service.chat_nutrition(
        message=payload.message,
        history=history_dicts
    )

    return NutritionChatResponse(
        source="nutrition",
        reply=reply,
        status="success"
    )
