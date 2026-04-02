"""Pydantic models for ContextBudget API."""

from pydantic import BaseModel


class TokenCategories(BaseModel):
    system: int = 0
    history: int = 0
    tools: int = 0
    current: int = 0


class TrackEvent(BaseModel):
    session_id: str
    provider: str
    categories: TokenCategories
    total: int
    limit: int
    timestamp: str


class TrackResponse(BaseModel):
    status: str = "ok"
    session_id: str
    usage_pct: float


class SessionSummary(BaseModel):
    total_tokens: int
    by_category: dict[str, int]
    usage_pct: float
    alerts_triggered: int


class SessionResponse(BaseModel):
    session_id: str
    events: list[dict]
    summary: SessionSummary


class AlertConfig(BaseModel):
    session_id: str
    thresholds: list[int] = [70, 85, 95]
    webhook_url: str | None = None


class AlertConfigResponse(BaseModel):
    status: str = "ok"
    session_id: str
    thresholds: list[int]


class CheckoutRequest(BaseModel):
    tier: str  # "pro" or "team"


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
