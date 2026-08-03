from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.credit import (
    CreditApplicationRequest,
    Decision,
    RiskLevel,
)

ExplanationProvider = Literal["local", "openai"]

FactorDirection = Literal["positive", "negative", "neutral"]


class CreditExplanationRequest(BaseModel):
    """Request schema for generating a credit decision explanation."""

    application: CreditApplicationRequest = Field(
        ...,
        description="Credit application data to be scored and explained.",
    )


class ExplanationFactor(BaseModel):
    """A human-readable factor contributing to the explanation."""

    feature: str
    title: str
    direction: FactorDirection
    description: str


class CreditExplanationResponse(BaseModel):
    """Response schema for explainable credit scoring."""

    request_id: str
    credit_score: int
    default_probability: float
    risk_level: RiskLevel
    decision: Decision

    summary: str = Field(
        ...,
        description="Short summary of the credit decision.",
    )

    customer_message: str = Field(
        ...,
        description="Respectful customer-facing explanation.",
    )

    employee_note: str = Field(
        ...,
        description="Operational note for bank employee.",
    )

    factors: list[ExplanationFactor] = Field(
        default_factory=list,
        description="Main factors used in the explanation.",
    )

    recommendations: list[str] = Field(
        default_factory=list,
        description="Practical recommendations for improving credit outcome.",
    )

    generated_by: ExplanationProvider
    timestamp: datetime