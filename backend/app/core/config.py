import os
from pathlib import Path
from typing import Final

# Load environment variables from .env file BEFORE anything else.
# This must happen before reading any env var below.
from dotenv import load_dotenv

BACKEND_DIR: Final[Path] = Path(__file__).resolve().parents[2]

# Look for .env in the backend directory.
_ENV_FILE: Final[Path] = BACKEND_DIR / ".env"
if _ENV_FILE.exists():
    load_dotenv(dotenv_path=_ENV_FILE, override=False)

MODEL_PATH: Final[Path] = (
    BACKEND_DIR / "models" / "credit_scoring_pipeline.joblib"
)

FEATURE_IMPORTANCE_PATH: Final[Path] = (
    BACKEND_DIR / "models" / "feature_importance.csv"
)

API_V1_PREFIX: Final[str] = "/api/v1"

PROJECT_NAME: Final[str] = "CreditWise API"
PROJECT_VERSION: Final[str] = "0.1.0"

EXPLANATION_PROVIDER: Final[str] = (
    os.getenv("EXPLANATION_PROVIDER", "local").strip().lower()
)

# Base URL for any OpenAI-compatible endpoint.
# Defaults to a local self-hosted LLM for privacy-preserving explanations.
OPENAI_BASE_URL: Final[str] = (
    os.getenv("OPENAI_BASE_URL", "http://localhost:20128/v1").strip()
)

OPENAI_API_KEY: Final[str] = os.getenv("OPENAI_API_KEY", "").strip()

OPENAI_MODEL: Final[str] = (
    os.getenv("OPENAI_MODEL", "oc/deepseek-v4-flash-free").strip()
)

EXPLANATION_LANGUAGE: Final[str] = (
    os.getenv("EXPLANATION_LANGUAGE", "fa").strip().lower()
)