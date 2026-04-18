"""
api/schemas.py — request/response Pydantic models.

Only three families of schemas live here:

  1. Query   — the chat endpoint's request envelope.
  2. Auth    — register / login / refresh / token.
  3. Chat    — conversation + message shapes returned to the client.

The engine's result envelope (`PlanResponse`, `AnswerResponse`,
`ErrorResponse`) is documented here too, even though the `/api/query`
handler returns the dict as-is — tests validate against these models
and they anchor the Python-side type contract that mirrors the
frontend's `types/index.ts`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Union

from pydantic import BaseModel, EmailStr


# ── Query (chat) ──

class QueryRequest(BaseModel):
    message: str
    conversation_id: int


# ── Auth ──

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Conversations ──

class ConversationCreate(BaseModel):
    title: str = "New conversation"


class ConversationUpdate(BaseModel):
    title: str


class ConversationOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    response_data: dict | None = None
    created_at: datetime


# ── Engine result envelope ──
#
# These mirror the shape returned by Orchestrator.handle(). The
# handler returns `dict` so FastAPI does not validate or filter, but
# tests and OpenAPI consumers can reference these models.

class RouteStep(BaseModel):
    type: Literal["ride", "transfer"]
    line: str | None = None
    board: str | None = None
    alight: str | None = None
    stations: list[str] | None = None
    # Present only for `transfer` steps.
    from_: str | None = None  # serialized as "from"
    to: str | None = None

    class Config:
        populate_by_name = True


class ViolationStep(BaseModel):
    type: str
    from_: str | None = None
    to: str | None = None


class AuditEntry(BaseModel):
    candidate: str
    violations: list[dict]


class TimeContext(BaseModel):
    weekday: str
    hour: int
    minute: int
    display: str


# Fiscal reasoning — the symbolic-repair surface.

class BudgetContext(BaseModel):
    max_thb: int


class FareSegment(BaseModel):
    """One maximal same-agency run; exactly one fare per segment."""
    agency: str
    tap_in: str
    tap_out: str
    fare: int


class RepairStep(BaseModel):
    """One iteration of the diagnose→propose→replan loop.

    `diagnosis` and `repair_applied` are kept as loose dicts because
    Prolog authors them as structured terms with shape-variant content
    (over_budget vs within_budget; avoid_specific_boundary vs
    avoid_agency_pair vs force_single_agency vs infeasible)."""
    diagnosis: dict
    repair_applied: dict


class BudgetAuditEntry(BaseModel):
    """A candidate POI whose every repair chain still busted the budget.

    `certificate` is the Prolog-authored constructive infeasibility proof
    (repairs_exhausted, final_over_by, min_seen, and optional
    fare_unknown / graph_disconnected witnesses)."""
    candidate: str
    certificate: dict
    repair_trail: list[RepairStep] = []


class ExploreAlternative(BaseModel):
    """Rich explore-mode alternative — a fully-planned survivor.

    When `explore: true`, PlanData.alternatives is a list of these
    instead of a list of names: every survivor gets its own time,
    fare, steps, and (if repair fired) repair_trail."""
    name: str
    station: str
    total_time: int
    steps: list[dict] = []
    preference_score: int | None = None
    total_fare: int | None = None
    fare_breakdown: list[FareSegment] | None = None
    repair_trail: list[RepairStep] | None = None


class PlanData(BaseModel):
    origin: str
    destination: str | None = None
    poi: str | None = None
    total_time: int | None = None
    steps: list[dict] = []
    preference_score: int | None = None
    time_context: TimeContext | None = None
    budget_context: BudgetContext | None = None
    total_fare: int | None = None
    fare_breakdown: list[FareSegment] | None = None
    repair_trail: list[RepairStep] | None = None
    budget_audit: list[BudgetAuditEntry] | None = None
    relaxation_note: list[str] | None = None
    audit_trail: list[AuditEntry] | None = None
    alternatives: list[ExploreAlternative] | list[str] | None = None
    explore: bool | None = None
    unknown_tags: list[str] | None = None
    note: str | None = None
    answer: str | None = None


class AnswerData(BaseModel):
    answer: str


class ErrorData(BaseModel):
    message: str


class PlanResponse(BaseModel):
    type: Literal["plan"]
    data: PlanData


class AnswerResponse(BaseModel):
    type: Literal["answer"]
    data: AnswerData


class ErrorResponse(BaseModel):
    type: Literal["error"]
    data: ErrorData


QueryResult = Union[PlanResponse, AnswerResponse, ErrorResponse]


# ── Data endpoints ──

class StationInfo(BaseModel):
    name: str
    lines: list[str]


class AttractionInfo(BaseModel):
    name: str
    station: str
    tags: list[str] = []
