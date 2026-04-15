from fastapi import APIRouter, Depends, HTTPException, Request
from google.genai import types
from sqlalchemy.orm import Session

from api.schemas import QueryRequest
from auth.dependencies import get_current_user
from db import crud
from db.database import get_db
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


def _extract_answer_and_blob(result: dict) -> tuple[str, dict | None]:
    """Return (text_to_persist_as_content, structured_response_data).

    The engine returns one of three envelope types:
      - "plan":   data has an `answer` (LLM narration) + structured fields.
      - "answer": data has an `answer` (plain text response).
      - "error":  data has a `message`.

    For `plan`, we persist the narration as the message content so the
    frontend can render it as markdown fallback if it doesn't understand
    the structured view, and keep the full result as `response_data` for
    rich rendering.
    """
    rtype = result.get("type")
    data = result.get("data", {}) or {}
    if rtype == "error":
        return data.get("message", ""), None
    if rtype == "answer":
        return data.get("answer", "") or "", None
    if rtype == "plan":
        narration = data.get("answer") or ""
        return narration, result
    return "", None


@router.post("/query")
async def query(
    body: QueryRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    orchestrator = request.app.state.orchestrator

    conversation = crud.get_conversation(db, body.conversation_id, user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db_messages = crud.get_messages_for_conversation(db, body.conversation_id)
    history = _rebuild_history(db_messages)

    result, _ = orchestrator.handle(body.message, history)

    crud.add_message(db, body.conversation_id, "user", body.message)

    answer_text, response_data = _extract_answer_and_blob(result)
    if answer_text or response_data:
        crud.add_message(
            db,
            body.conversation_id,
            "model",
            answer_text,
            response_data=response_data,
        )

    crud.touch_conversation(db, body.conversation_id)
    return result
