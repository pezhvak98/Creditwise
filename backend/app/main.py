from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.credit import router as credit_router
from app.core.config import API_V1_PREFIX, PROJECT_NAME, PROJECT_VERSION
from app.services.credit_service import CreditScoringService
from app.services.explanation_service import ExplanationService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML artifacts and services when the API starts."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    logger.info("Starting CreditWise API...")

    credit_service = CreditScoringService()
    credit_service.load()

    explanation_service = ExplanationService()

    app.state.credit_service = credit_service
    app.state.explanation_service = explanation_service

    logger.info(
        "CreditWise API is ready. Explanation provider: %s",
        explanation_service.provider,
    )

    yield

    logger.info("Shutting down CreditWise API.")


app = FastAPI(
    title=PROJECT_NAME,
    version=PROJECT_VERSION,
    description=(
        "CreditWise is an explainable alternative credit scoring API. "
        "It predicts credit risk using alternative financial behavior data "
        "and generates human-friendly explanations."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(credit_router, prefix=API_V1_PREFIX)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    """Basic API information."""
    return {
        "project": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
def health(request: Request) -> dict[str, object]:
    """Health check endpoint."""
    credit_service = getattr(request.app.state, "credit_service", None)
    explanation_service = getattr(request.app.state, "explanation_service", None)

    model_ready = bool(credit_service and credit_service.is_ready)
    explanation_ready = bool(explanation_service is not None)

    return {
        "status": "ok",
        "model_ready": model_ready,
        "explanation_ready": explanation_ready,
        "version": PROJECT_VERSION,
    }