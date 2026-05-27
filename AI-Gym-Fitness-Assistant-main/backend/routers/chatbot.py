"""
backend/routers/chatbot.py – Virtual Gym Buddy conversational endpoints.
"""
from fastapi import APIRouter
from backend.schemas import ChatMessage, ChatResponse
from models.gym_buddy import GymBuddy, simple_sentiment

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

# One buddy instance per session_id
_buddies: dict[str, GymBuddy] = {}


def _get_buddy(session_id: str) -> GymBuddy:
    if session_id not in _buddies:
        _buddies[session_id] = GymBuddy()
    return _buddies[session_id]


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatMessage):
    """Send a message and get a fitness-focused reply."""
    buddy = _get_buddy(payload.session_id or "default")
    reply = buddy.chat(payload.message)
    sentiment = simple_sentiment(payload.message)
    return ChatResponse(reply=reply, sentiment=sentiment)


@router.post("/reset/{session_id}")
def reset_chat(session_id: str):
    """Clear conversation history for a session."""
    if session_id in _buddies:
        _buddies[session_id].clear_history()
    return {"status": "cleared"}
