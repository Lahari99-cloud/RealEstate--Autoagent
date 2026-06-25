from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, TypedDict

from pydantic import BaseModel, Field


class Purpose(str, Enum):
    investment = "investment"
    end_use = "end_use"


class Lead(BaseModel):
    budget_aed: int = Field(gt=0)
    preferred_areas: list[str] = Field(min_length=1)
    bedrooms: int | None = Field(default=None, ge=0, le=10)
    purpose: Purpose = Purpose.investment
    timeline: str = "flexible"
    nationality: str | None = None
    language: str = "English"
    must_haves: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0, le=1)


class Listing(BaseModel):
    id: str
    title: str
    area: str
    bedrooms: int
    price_aed: int
    size_sqft: int
    annual_rent_aed: int
    service_charge_aed: int
    status: str
    amenities: list[str]
    description: str


class Recommendation(BaseModel):
    listing: Listing
    match_score: float
    estimated_market_value_aed: int
    discount_to_market_pct: float
    gross_yield_pct: float
    net_yield_pct: float
    annual_cash_flow_aed: int
    down_payment_aed: int = 0
    estimated_loan_aed: int = 0
    monthly_payment_aed: int = 0
    income_required_aed: int = 0
    affordability_note: str = ""
    area_rationale: str = ""
    nearby: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)


class LeadQualification(BaseModel):
    score: int = Field(ge=0, le=100)
    intent: str
    budget_confidence: str
    timeline_urgency: str
    financing_readiness: str
    crm_stage: str
    handoff_summary: str
    next_best_action: str


class ComplianceReview(BaseModel):
    jurisdiction: str = "UAE"
    summary: str
    required_checks: list[str] = Field(default_factory=list)
    disclaimers: list[str] = Field(default_factory=list)
    risk_level: str


class ConversationTurn(BaseModel):
    role: str
    content: str
    run_id: str | None = None
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TraceEvent(BaseModel):
    sequence: int
    agent: str
    status: str = "completed"
    summary: str
    duration_ms: int
    confidence: float | None = None
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InquiryRequest(BaseModel):
    inquiry: str = Field(min_length=8, max_length=4000)
    require_approval: bool = True
    conversation_id: str | None = Field(default=None, max_length=100)


class ApprovalRequest(BaseModel):
    approved: bool
    reviewer: str = Field(min_length=2, max_length=100)
    note: str | None = Field(default=None, max_length=500)


class RunResponse(BaseModel):
    run_id: str
    status: str
    conversation_id: str | None = None
    lead: Lead | None = None
    qualification: LeadQualification | None = None
    compliance: ComplianceReview | None = None
    recommendations: list[Recommendation] = Field(default_factory=list)
    trace: list[TraceEvent] = Field(default_factory=list)
    approval_url: str | None = None
    pdf_url: str | None = None


class AgentState(TypedDict, total=False):
    run_id: str
    inquiry: str
    conversation_id: str
    memory_context: list[dict[str, Any]]
    require_approval: bool
    lead: dict[str, Any]
    qualification: dict[str, Any]
    compliance: dict[str, Any]
    matches: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    trace: list[dict[str, Any]]
    approval: dict[str, Any]
    pdf_path: str
    status: str
