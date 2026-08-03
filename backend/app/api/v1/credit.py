import logging

from fastapi import APIRouter, HTTPException, Request

from app.schemas.credit import CreditApplicationRequest, CreditScoreResponse

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