import logging

from fastapi import APIRouter, HTTPException, Request

from app.schemas.credit import (
    CreditApplicationRequest,
    CreditScoreResponse,
)
from app.schemas.explanation import (
    CreditExplanationRequest,
    CreditExplanationResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/credit", tags=["Credit"])


@router.post(
    "/score",
    response_model=CreditScoreResponse,
    summary="Score a customer using alternative credit data",
)
def score_credit(
    application: CreditApplicationRequest,
    request: Request,
) -> CreditScoreResponse:
    """Score a credit application using the trained ML pipeline."""
    service = request.app.state.credit_service

    try:
        return service.predict(application)
    except Exception as exc:
        logger.exception("Credit scoring request failed.")
        raise HTTPException(
            status_code=500,
            detail="Credit scoring request failed.",
        ) from exc


@router.post(
    "/explain",
    response_model=CreditExplanationResponse,
    summary="Generate an explainable credit decision",
)
def explain_credit(
    payload: CreditExplanationRequest,
    request: Request,
) -> CreditExplanationResponse:
    """Score an application and generate a human-friendly explanation."""
    credit_service = request.app.state.credit_service
    explanation_service = request.app.state.explanation_service

    try:
        score_response = credit_service.predict(payload.application)

        return explanation_service.explain(
            application=payload.application,
            score_response=score_response,
        )
    except Exception as exc:
        logger.exception("Credit explanation request failed.")
        raise HTTPException(
            status_code=500,
            detail="Credit explanation request failed.",
        ) from exc