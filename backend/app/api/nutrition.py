"""
Nutrition AI Route Placeholders.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/nutrition", tags=["Nutrition AI"])


class ConversationRequest(BaseModel):
    patient_id: str
    message: str


@router.post("/chat")
async def nutrition_chat(payload: ConversationRequest):
    """
    Nutrition AI conversation endpoint placeholder.
    Handles food habits, meal patterns, appetite, hydration, and physical lifestyle.
    """
    return {
        "source": "nutrition",
        "reply": f"[Nutrition AI Placeholder] Received message from patient {payload.patient_id}. Conversation logic scheduled for Days 1-3.",
        "extracted_context_count": 0
    }
