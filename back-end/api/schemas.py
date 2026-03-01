from datetime import datetime
from pydantic import BaseModel, EmailStr


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
    created_at: datetime


# ── Existing route/station schemas ──

class RouteStep(BaseModel):
    type: str
    line: str | None = None
    board: str | None = None
    alight: str | None = None
    stations: list[str] | None = None
    from_station: str | None = None
    to_station: str | None = None


class RouteData(BaseModel):
    from_station: str
    to_station: str
    total_time: int
    steps: list[RouteStep]


class StationInfo(BaseModel):
    name: str
    lines: list[str]


class AttractionInfo(BaseModel):
    name: str
    station: str
