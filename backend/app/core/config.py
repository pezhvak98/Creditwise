from pathlib import Path
from typing import Final

BACKEND_DIR: Final[Path] = Path(__file__).resolve().parents[2]

MODEL_PATH: Final[Path] = (
    BACKEND_DIR / "models" / "credit_scoring_pipeline.joblib"
)

FEATURE_IMPORTANCE_PATH: Final[Path] = (
    BACKEND_DIR / "models" / "feature_importance.csv"
)

API_V1_PREFIX: Final[str] = "/api/v1"

PROJECT_NAME: Final[str] = "CreditWise API"
PROJECT_VERSION: Final[str] = "0.1.0"