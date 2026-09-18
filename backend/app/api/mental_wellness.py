"""
PCIF Mental Wellness AI API Routes.
Provides patient-facing conversational endpoints for stress, sleep, mood, and mental wellbeing guidance,
integrated with automatic CCEE context extraction and MongoDB patient_context persistence.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from backend.app.services.llm_service import llm_service
from backend.app.services.context_persistence_service import context_persistence_service

router = APIRouter(prefix="/mental-wellness", tags=["Mental Wellness AI"])


class ChatTurn(BaseModel):
    role: str = Field(..., description="Role of the speaker: 'user' or 'assistant'")
    content: str = Field(..., description="Turn text content")


class MentalWellnessChatRequest(BaseModel):
    patient_id: str = Field(..., description="Opaque session identifier for the active patient")
    message: str = Field(..., description="Current patient input message")
    history: List[ChatTurn] = Field(
        default_factory=list,
        description="Temporary in-memory conversation history for the active session"
    )

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("patient_id is required and cannot be empty or whitespace-only.")
        return v.strip()

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("message is required and cannot be empty or whitespace-only.")
        return v.strip()


class ContextPersistenceMetadata(BaseModel):
    status: str = Field(..., description="Persistence status: 'saved', 'no_relevant_context', or 'failed'")
    saved_count: int = Field(0, description="Number of clinical context items persisted")


class MentalWellnessChatResponse(BaseModel):
    source: str = "mental_wellness"
    reply: str
    status: str = "success"
    context_persistence: Optional[ContextPersistenceMetadata] = None


@router.post("/chat", response_model=MentalWellnessChatResponse)
async def mental_wellness_chat(payload: MentalWellnessChatRequest):
    """
    Mental Wellness AI conversational chat endpoint.
    Statelessly processes multi-turn context sent by the client.
    1. Generates patient-facing AI response using Gemini Interactions API (store=False).
    2. Runs frozen CCEE extraction on role-aware history + current user turn.
    3. Persists validated ClinicalContextItem objects to MongoDB patient_context collection.
    """
    history_dicts = [{"role": turn.role, "content": turn.content} for turn in payload.history]

    # Generate patient-facing AI response
    try:
        reply = llm_service.chat_mental_wellness(
            message=payload.message,
            history=history_dicts
        )
    except Exception as e:
        # If chat generation fails, preserve existing chat error behavior and do NOT run CCEE
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mental Wellness AI chat generation failed: {str(e)}"
        ) from e

    # CCEE input construction: role-aware history + current user message
    # IMPORTANT: The newly generated assistant answer is NOT appended as patient evidence.
    ccee_conversation = list(history_dicts)
    ccee_conversation.append({"role": "user", "content": payload.message})

    # Trigger context persistence orchestration
    persistence_res = context_persistence_service.extract_and_persist_context(
        patient_id=payload.patient_id,
        conversation=ccee_conversation,
        source="mental_wellness"
    )

    return MentalWellnessChatResponse(
        source="mental_wellness",
        reply=reply,
        status="success",
        context_persistence=ContextPersistenceMetadata(
            status=persistence_res.status,
            saved_count=persistence_res.saved_count
        )
    )
