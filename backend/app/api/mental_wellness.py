"""
PCIF Mental Wellness AI API Routes.
Provides patient-facing conversational endpoints for stress, sleep, mood, and mental wellbeing guidance.
"""

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.app.services.llm_service import llm_service

router = APIRouter(prefix="/mental-wellness", tags=["Mental Wellness AI"])


class ChatTurn(BaseModel):
    role: str = Field(..., description="Role of the speaker: 'user' or 'assistant'")
    content: str = Field(..., description="Turn text content")


class MentalWellnessChatRequest(BaseModel):
    message: str = Field(..., description="Current patient input message")
    history: List[ChatTurn] = Field(
        default_factory=list,
        description="Temporary in-memory conversation history for the active session"
    )


class MentalWellnessChatResponse(BaseModel):
    source: str = "mental_wellness"
    reply: str
    status: str = "success"


@router.post("/chat", response_model=MentalWellnessChatResponse)
async def mental_wellness_chat(payload: MentalWellnessChatRequest):
    """
    Mental Wellness AI conversational chat endpoint.
    Statelessly processes multi-turn context sent by the client.
    Gemini Interactions persistence is disabled using store=False, and PCIF does not persist raw conversations in its own database during the current prototype.
    """
    history_dicts = [{"role": turn.role, "content": turn.content} for turn in payload.history]

    reply = llm_service.chat_mental_wellness(
        message=payload.message,
        history=history_dicts
    )

    return MentalWellnessChatResponse(
        source="mental_wellness",
        reply=reply,
        status="success"
    )

