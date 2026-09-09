"""
Mental Wellness AI Route Placeholders.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/mental-wellness", tags=["Mental Wellness AI"])


class ConversationRequest(BaseModel):
    patient_id: str
    message: str


@router.post("/chat")
async def mental_wellness_chat(payload: ConversationRequest):
    """
    Mental Wellness AI conversation endpoint placeholder.
    Handles mood, stress, sleep, anxiety, and emotional wellness.
    """
    return {
        "source": "mental_wellness",
        "reply": f"[Mental Wellness AI Placeholder] Received message from patient {payload.patient_id}. Conversation logic scheduled for Days 1-3.",
        "extracted_context_count": 0
    }
