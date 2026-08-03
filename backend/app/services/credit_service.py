from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

from app.core.config import (
    FEATURE_IMPORTANCE_PATH,
    MODEL_PATH,
    PROJECT_VERSION,
)
from app.core.features import FEATURE_COLUMNS
from app.schemas.credit import (
    CreditApplicationRequest,
    CreditScoreResponse,
    Decision,
    FeatureFactor,
    RiskLevel,
)

logger = logging.getLogger(__name__)

LOW_RISK_THRESHOLD: float = 0.15
MEDIUM_RISK_THRESHOLD: float = 0.30

MIN_CREDIT_SCORE: int = 300
MAX_CREDIT_SCORE: int = 850


class CreditScoringService:
    """Service responsible for loading the ML pipeline and scoring requests."""

    def __init__(self) -> None:
        self.pipeline: Optional[Pipeline] = None
        self.top_factors: list[FeatureFactor] = []
        self.is_ready: bool = False

    def load(self) -> None:
        """Load model and feature importance artifacts."""
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model artifact not found at {MODEL_PATH}. "
                "Please run Phase 2 training first."
            )

        self.pipeline = joblib.load(MODEL_PATH)
        self.top_factors = self._load_top_factors()
        self.is_ready = True

        logger.info("Credit scoring model loaded from: %s", MODEL_PATH)
        logger.info("Loaded %s global top factors.", len(self.top_factors))

    def _load_top_factors(self) -> list[FeatureFactor]:
        """Load top global feature importance factors if available."""
        try:
            if not FEATURE_IMPORTANCE_PATH.exists():
                logger.warning(
                    "Feature importance file not found at: %s",
                    FEATURE_IMPORTANCE_PATH,
                )
                return []

            df = pd.read_csv(FEATURE_IMPORTANCE_PATH, encoding="utf-8-sig")

            required_columns = {"feature", "importance_normalized"}

            if not required_columns.issubset(df.columns):
                logger.warning(
                    "Feature importance file is missing required columns."
                )
                return []

            df = df.sort_values(
                by="importance_normalized",
                ascending=False,
            ).head(5)

            factors: list[FeatureFactor] = []

            for _, row in df.iterrows():
                factors.append(
                    FeatureFactor(
                        feature=str(row["feature"]),
                        importance_normalized=float(row["importance_normalized"]),
                    )
                )

            return factors

        except Exception:
            logger.exception("Failed to load feature importance file.")
            return []

    def predict(self, application: CreditApplicationRequest) -> CreditScoreResponse:
        """Generate credit score, risk level, and decision for one application."""
        if not self.is_ready or self.pipeline is None:
            raise RuntimeError("Credit scoring service is not ready.")

        input_row = self._to_model_input(application)

        df = pd.DataFrame(
            data=[input_row],
            columns=list(FEATURE_COLUMNS),
        )

        default_probability = float(
            self.pipeline.predict_proba(df)[:, 1][0]
        )

        credit_score = self._probability_to_score(default_probability)
        risk_level = self._risk_level(default_probability)
        decision = self._decision(default_probability)
        request_id = str(uuid.uuid4())

        logger.info(
            "request_id=%s | default_probability=%.4f | decision=%s",
            request_id,
            default_probability,
            decision,
        )

        return CreditScoreResponse(
            request_id=request_id,
            credit_score=credit_score,
            default_probability=default_probability,
            risk_level=risk_level,
            decision=decision,
            top_factors=self.top_factors,
            model_version=PROJECT_VERSION,
            timestamp=datetime.now(timezone.utc),
        )

    @staticmethod
    def _to_model_input(application: CreditApplicationRequest) -> dict[str, object]:
        """Convert API request to the exact model input schema."""
        rent_payment_on_time_rate: Optional[float] = None

        if application.has_rent_history:
            rent_payment_on_time_rate = application.rent_payment_on_time_rate

        return {
            "age": application.age,
            "monthly_income": application.monthly_income,
            "months_at_current_address": application.months_at_current_address,
            "number_of_dependents": application.number_of_dependents,
            "has_rent_history": int(application.has_rent_history),
            "rent_payment_on_time_rate": rent_payment_on_time_rate,
            "utility_payment_on_time_rate": application.utility_payment_on_time_rate,
            "telecom_payment_on_time_rate": application.telecom_payment_on_time_rate,
            "monthly_avg_telco_charge": application.monthly_avg_telco_charge,
            "ecommerce_activity_score": application.ecommerce_activity_score,
            "digital_wallet_usage_score": application.digital_wallet_usage_score,
            "savings_behavior_score": application.savings_behavior_score,
            "employment_type": application.employment_type,
        }

    @staticmethod
    def _probability_to_score(default_probability: float) -> int:
        """Map default probability to a simple credit score.

        Higher default probability results in a lower credit score.
        """
        score = MIN_CREDIT_SCORE + (MAX_CREDIT_SCORE - MIN_CREDIT_SCORE) * (
            1.0 - default_probability
        )

        return int(round(max(MIN_CREDIT_SCORE, min(MAX_CREDIT_SCORE, score))))

    @staticmethod
    def _risk_level(default_probability: float) -> RiskLevel:
        """Map default probability to a business risk level."""
        if default_probability <= LOW_RISK_THRESHOLD:
            return "low"

        if default_probability <= MEDIUM_RISK_THRESHOLD:
            return "medium"

        return "high"

    @staticmethod
    def _decision(default_probability: float) -> Decision:
        """Map default probability to a simplified business decision."""
        if default_probability <= LOW_RISK_THRESHOLD:
            return "approve"

        if default_probability <= MEDIUM_RISK_THRESHOLD:
            return "review"

        return "decline"