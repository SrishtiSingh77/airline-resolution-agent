from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services import agent

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    return agent.handle_message(payload.booking_reference, payload.message)