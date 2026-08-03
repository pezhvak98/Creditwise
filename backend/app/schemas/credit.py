from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

EmploymentType = Literal[
    "salaried",
    "self_employed",
    "contract",
    "gig",
    "retired",
    "unemployed",
]

RiskLevel = Literal["low", "medium", "high"]
Decision = Literal["approve", "review", "decline"]


class CreditApplicationRequest(BaseModel):
    """Input schema for alternative credit scoring."""

    customer_id: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Optional customer identifier.",
    )

    age: int = Field(
        ...,
        ge=18,
        le=100,
        description="Customer age.",
    )

    employment_type: EmploymentType = Field(
        ...,
        description="Employment type used as a categorical feature.",
    )

    monthly_income: float = Field(
        ...,
        ge=0,
        description="Synthetic monthly income in arbitrary units.",
    )

    months_at_current_address: int = Field(
        ...,
        ge=0,
        le=600,
        description="Number of months at current address.",
    )

    number_of_dependents: int = Field(
        ...,
        ge=0,
        le=20,
        description="Number of financial dependents.",
    )

    has_rent_history: bool = Field(
        ...,
        description="Whether the customer has rent payment history.",
    )

    rent_payment_on_time_rate: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="On-time rent payment ratio between 0 and 1.",
    )

    utility_payment_on_time_rate: float = Field(
        ...,
        ge=0,
        le=1,
        description="On-time utility payment ratio between 0 and 1.",
    )

    telecom_payment_on_time_rate: float = Field(
        ...,
        ge=0,
        le=1,
        description="On-time telecom payment ratio between 0 and 1.",
    )

    monthly_avg_telco_charge: float = Field(
        ...,
        ge=0,
        description="Average monthly telecom charge.",
    )

    ecommerce_activity_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="E-commerce activity score between 0 and 100.",
    )

    digital_wallet_usage_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Digital wallet usage score between 0 and 100.",
    )

    savings_behavior_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Savings behavior score between 0 and 100.",
    )

    @model_validator(mode="after")
    def normalize_rent_history(self) -> "CreditApplicationRequest":
        """If there is no rent history, rent rate must be treated as missing."""
        if not self.has_rent_history:
            self.rent_payment_on_time_rate = None
        return self


class FeatureFactor(BaseModel):
    """A global model factor used for basic explainability."""

    feature: str
    importance_normalized: float


class CreditScoreResponse(BaseModel):
    """Output schema for credit scoring."""

    request_id: str
    credit_score: int
    default_probability: float
    risk_level: RiskLevel
    decision: Decision
    top_factors: list[FeatureFactor]
    model_version: str
    timestamp: datetime