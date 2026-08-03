from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logger = logging.getLogger(__name__)

DEFAULT_DATASET_PATH: Final[Path] = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "synthetic_alternative_credit_dataset.csv"
)

DEFAULT_MODEL_DIR: Final[Path] = (
    Path(__file__).resolve().parents[1] / "models"
)

ID_COLUMN: Final[str] = "customer_id"
NAME_COLUMN: Final[str] = "customer_name"
TARGET_COLUMN: Final[str] = "is_default_12m"

CATEGORICAL_FEATURES: Final[tuple[str, ...]] = (
    "employment_type",
)

NUMERIC_FEATURES: Final[tuple[str, ...]] = (
    "age",
    "monthly_income",
    "months_at_current_address",
    "number_of_dependents",
    "has_rent_history",
    "rent_payment_on_time_rate",
    "utility_payment_on_time_rate",
    "telecom_payment_on_time_rate",
    "monthly_avg_telco_charge",
    "ecommerce_activity_score",
    "digital_wallet_usage_score",
    "savings_behavior_score",
)

MODEL_FILE_NAME: Final[str] = "credit_scoring_pipeline.joblib"
METRICS_FILE_NAME: Final[str] = "evaluation_metrics.json"
FEATURE_IMPORTANCE_FILE_NAME: Final[str] = "feature_importance.csv"
METADATA_FILE_NAME: Final[str] = "training_metadata.json"


@dataclass(frozen=True)
class TrainConfig:
    """Configuration for model training."""

    dataset_path: Path
    model_dir: Path
    model_type: str
    test_size: float
    random_state: int

    def validate(self) -> None:
        """Validate training configuration."""
        if self.model_type not in {"logistic", "rf"}:
            raise ValueError("model_type must be either 'logistic' or 'rf'.")

        if not 0.0 < self.test_size < 1.0:
            raise ValueError("test_size must be between 0 and 1.")

        if self.random_state < 0:
            raise ValueError("random_state must be non-negative.")


def load_dataset(path: Path) -> pd.DataFrame:
    """Load dataset and validate required columns."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}. "
            "Please run Phase 1 synthetic data generation first."
        )

    df = pd.read_csv(path, encoding="utf-8-sig")

    required_columns = {
        ID_COLUMN,
        TARGET_COLUMN,
        *CATEGORICAL_FEATURES,
        *NUMERIC_FEATURES,
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    df[TARGET_COLUMN] = pd.to_numeric(df[TARGET_COLUMN], errors="coerce")

    missing_target_count = int(df[TARGET_COLUMN].isna().sum())

    if missing_target_count > 0:
        logger.warning(
            "Dropping %s rows with missing target values.",
            missing_target_count,
        )
        df = df.dropna(subset=[TARGET_COLUMN])

    if df.empty:
        raise ValueError("Dataset is empty after removing rows with missing target.")

    return df


def build_preprocessor() -> ColumnTransformer:
    """Build preprocessing pipeline for numeric and categorical features."""
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, list(NUMERIC_FEATURES)),
            ("cat", categorical_pipeline, list(CATEGORICAL_FEATURES)),
        ]
    )

    return preprocessor


def build_estimator(model_type: str, random_state: int):
    """Build the classification estimator based on selected model type."""
    if model_type == "logistic":
        return LogisticRegression(
            max_iter=1000,
            solver="lbfgs",
            class_weight="balanced",
            random_state=random_state,
        )

    return RandomForestClassifier(
        n_estimators=300,
        min_samples_leaf=20,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )


def build_pipeline(model_type: str, random_state: int) -> Pipeline:
    """Build full ML pipeline including preprocessing and model."""
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("model", build_estimator(model_type, random_state)),
        ]
    )


def extract_feature_names(pipeline: Pipeline) -> list[str]:
    """Extract transformed feature names from the fitted preprocessor."""
    preprocessor = pipeline.named_steps["preprocessor"]
    raw_feature_names = preprocessor.get_feature_names_out()

    feature_names: list[str] = []

    for name in raw_feature_names:
        name = str(name)

        # ColumnTransformer names usually look like:
        # num__age
        # cat__employment_type_salaried
        if "__" in name:
            name = name.split("__")[-1]

        feature_names.append(name)

    return feature_names


def extract_feature_importance(
    pipeline: Pipeline,
    model_type: str,
) -> pd.DataFrame:
    """Extract feature importance from the fitted model."""
    model = pipeline.named_steps["model"]
    feature_names = extract_feature_names(pipeline)

    if model_type == "logistic":
        coefficients = np.asarray(model.coef_[0])

        if len(coefficients) != len(feature_names):
            logger.warning(
                "Feature name length does not match coefficient length. "
                "Using generic feature names."
            )
            feature_names = [f"feature_{i}" for i in range(len(coefficients))]

        importance_df = pd.DataFrame(
            {
                "feature": feature_names,
                "signed_coefficient": coefficients,
                "importance": np.abs(coefficients),
            }
        )
    else:
        importances = np.asarray(model.feature_importances_)

        if len(importances) != len(feature_names):
            logger.warning(
                "Feature name length does not match feature importance length. "
                "Using generic feature names."
            )
            feature_names = [f"feature_{i}" for i in range(len(importances))]

        importance_df = pd.DataFrame(
            {
                "feature": feature_names,
                "importance": importances,
            }
        )

    importance_sum = float(importance_df["importance"].sum())

    importance_df["importance_normalized"] = (
        importance_df["importance"] / max(importance_sum, 1e-12)
    )

    importance_df = (
        importance_df.sort_values(by="importance", ascending=False)
        .reset_index(drop=True)
    )

    return importance_df


def evaluate_model(
    pipeline: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict[str, Any]:
    """Evaluate the fitted pipeline on the test set."""
    y_probability = pipeline.predict_proba(X_test)[:, 1]
    y_pred = pipeline.predict(X_test)

    report = classification_report(
        y_test,
        y_pred,
        output_dict=True,
        zero_division=0,
    )

    cm = confusion_matrix(y_test, y_pred)

    metrics: dict[str, Any] = {
        "roc_auc": float(roc_auc_score(y_test, y_probability)),
        "average_precision": float(average_precision_score(y_test, y_probability)),
        "default_rate_test": float(y_test.mean()),
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
    }

    return metrics


def json_default(value: Any) -> Any:
    """Convert non-JSON-serializable values to serializable Python types."""
    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    if isinstance(value, np.ndarray):
        return value.tolist()

    return str(value)


def save_json(payload: dict[str, Any], path: Path) -> None:
    """Save dictionary as formatted JSON file."""
    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            default=json_default,
        ),
        encoding="utf-8",
    )


def train(config: TrainConfig) -> None:
    """Run the full training workflow."""
    config.validate()

    logger.info("Loading dataset from: %s", config.dataset_path)
    df = load_dataset(config.dataset_path)

    feature_columns = list(NUMERIC_FEATURES) + list(CATEGORICAL_FEATURES)

    X = df[feature_columns]
    y = df[TARGET_COLUMN].astype(int)

    if y.nunique() < 2:
        raise ValueError("Target variable must contain at least two classes.")

    logger.info("Dataset rows: %s", df.shape[0])
    logger.info("Default rate: %.2f%%", float(y.mean()) * 100)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config.test_size,
        stratify=y,
        random_state=config.random_state,
    )

    logger.info("Train rows: %s", X_train.shape[0])
    logger.info("Test rows: %s", X_test.shape[0])

    pipeline = build_pipeline(
        model_type=config.model_type,
        random_state=config.random_state,
    )

    logger.info("Training model type: %s", config.model_type)
    pipeline.fit(X_train, y_train)

    metrics = evaluate_model(pipeline, X_test, y_test)
    feature_importance = extract_feature_importance(pipeline, config.model_type)

    config.model_dir.mkdir(parents=True, exist_ok=True)

    model_path = config.model_dir / MODEL_FILE_NAME
    metrics_path = config.model_dir / METRICS_FILE_NAME
    feature_importance_path = config.model_dir / FEATURE_IMPORTANCE_FILE_NAME
    metadata_path = config.model_dir / METADATA_FILE_NAME

    joblib.dump(pipeline, model_path)

    save_json(metrics, metrics_path)

    feature_importance.to_csv(
        feature_importance_path,
        index=False,
        encoding="utf-8-sig",
    )

    training_metadata: dict[str, Any] = {
        "model_type": config.model_type,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(config.dataset_path),
        "rows": int(df.shape[0]),
        "train_rows": int(X_train.shape[0]),
        "test_rows": int(X_test.shape[0]),
        "test_size": config.test_size,
        "random_state": config.random_state,
        "feature_columns": feature_columns,
        "excluded_columns": [ID_COLUMN, NAME_COLUMN, TARGET_COLUMN],
        "target_column": TARGET_COLUMN,
        "roc_auc": metrics["roc_auc"],
        "average_precision": metrics["average_precision"],
    }

    save_json(training_metadata, metadata_path)

    logger.info("Model saved at: %s", model_path)
    logger.info("Metrics saved at: %s", metrics_path)
    logger.info("Feature importance saved at: %s", feature_importance_path)
    logger.info("Training metadata saved at: %s", metadata_path)

    logger.info("ROC AUC: %.4f", metrics["roc_auc"])
    logger.info("Average Precision: %.4f", metrics["average_precision"])

    logger.info(
        "Top 10 important features:\n%s",
        feature_importance.head(10).to_string(index=False),
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Train CreditWise alternative credit scoring model."
    )

    parser.add_argument(
        "--dataset",
        dest="dataset_path",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Path to the synthetic credit dataset CSV.",
    )

    parser.add_argument(
        "--model-dir",
        dest="model_dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
        help="Directory to save model artifacts.",
    )

    parser.add_argument(
        "--model",
        dest="model_type",
        type=str,
        choices=["logistic", "rf"],
        default="logistic",
        help="Model type: logistic or random forest.",
    )

    parser.add_argument(
        "--test-size",
        dest="test_size",
        type=float,
        default=0.2,
        help="Fraction of data used for testing.",
    )

    parser.add_argument(
        "--seed",
        dest="random_state",
        type=int,
        default=42,
        help="Random state for reproducibility.",
    )

    return parser.parse_args()


def main() -> None:
    """Training entrypoint."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    args = parse_args()

    try:
        config = TrainConfig(
            dataset_path=args.dataset_path,
            model_dir=args.model_dir,
            model_type=args.model_type,
            test_size=args.test_size,
            random_state=args.random_state,
        )

        train(config)

    except Exception as exc:
        logger.error("Training failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()