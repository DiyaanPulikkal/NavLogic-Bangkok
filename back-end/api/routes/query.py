from fastapi import APIRouter, Request, Depends
from google.genai import types
from sqlalchemy.orm import Session

from api.schemas import QueryRequest
from auth.dependencies import get_current_user
from db.database import get_db
from db import crud
from db.models import User

router = APIRouter()


def _rebuild_history(messages) -> list:
    """Rebuild Gemini-compatible history from persisted plain-text messages."""
    history = []
    for msg in messages:
        role = msg.role if msg.role == "user" else "model"
        history.append(
            types.Content(role=role, parts=[types.Part(text=msg.content)])
        )
    return history


@router.post("/query")
async def query(
    body: QueryRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    orchestrator = request.app.state.orchestrator

    # Load existing messages and rebuild history
    db_messages = crud.get_messages_for_conversation(db, body.conversation_id)
    history = _rebuild_history(db_messages)

    result, _ = orchestrator.handle(body.message, history)

    # Persist user message and assistant response
    crud.add_message(db, body.conversation_id, "user", body.message)

    answer_text = ""
    response_data = None
    if result["type"] == "answer":
        answer_text = result["data"].get("answer", "")
    elif result["type"] == "error":
        answer_text = result["data"].get("message", "")
    elif result["type"] == "route":
        answer_text = f"Route from {result['data'].get('from', '')} to {result['data'].get('to', '')}"
        response_data = result
    elif result["type"] == "schedule":
        answer_text = result["data"].get("answer", f"Schedule from {result['data'].get('origin', '')} to {result['data'].get('destination', '')}")
        response_data = result
    elif result["type"] == "day_plan":
        stops = ", ".join(result["data"].get("stops", []))
        answer_text = result["data"].get("answer", f"Day plan: {stops}")
        response_data = result

    if answer_text:
        crud.add_message(db, body.conversation_id, "model", answer_text, response_data=response_data)

    crud.touch_conversation(db, body.conversation_id)

    return result
