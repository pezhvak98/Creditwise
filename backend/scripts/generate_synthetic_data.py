from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd
from faker import Faker

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_PATH: Final[Path] = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "synthetic_alternative_credit_dataset.csv"
)

EMPLOYMENT_TYPES: Final[tuple[str, ...]] = (
    "salaried",
    "self_employed",
    "contract",
    "gig",
    "retired",
    "unemployed",
)

EMPLOYMENT_PROBABILITIES: Final[tuple[float, ...]] = (
    0.38,
    0.22,
    0.18,
    0.10,
    0.06,
    0.06,
)

EMPLOYMENT_STABILITY: Final[dict[str, float]] = {
    "salaried": 0.82,
    "self_employed": 0.56,
    "contract": 0.61,
    "gig": 0.38,
    "retired": 0.76,
    "unemployed": 0.12,
}

EMPLOYMENT_INCOME_LOG_BASE: Final[dict[str, float]] = {
    "salaried": 7.00,
    "self_employed": 7.05,
    "contract": 6.90,
    "gig": 6.65,
    "retired": 6.60,
    "unemployed": 6.10,
}


@dataclass(frozen=True)
class GenerationConfig:
    """Configuration for synthetic dataset generation."""

    rows: int
    seed: int
    locale: str

    def validate(self) -> None:
        """Validate generation configuration values."""
        if self.rows <= 0:
            raise ValueError("rows must be a positive integer.")
        if not self.locale:
            raise ValueError("locale must not be empty.")


class SyntheticCreditDatasetGenerator:
    """Generates a deterministic synthetic alternative-credit dataset.

    The generator creates features that mimic alternative data sources
    such as rent, utilities, telecom, digital behavior, and savings habits.
    It also creates a synthetic target variable for 12-month default.

    No real customer data is used.
    """

    def __init__(self, config: GenerationConfig) -> None:
        self.config = config

        # Set Faker seed for reproducible synthetic names.
        Faker.seed(config.seed)

        try:
            self.faker = Faker(config.locale)
        except Exception as exc:
            logger.warning(
                "Faker locale '%s' is not available (%s). Falling back to 'en_US'.",
                config.locale,
                exc,
            )
            self.faker = Faker("en_US")

    def generate(self) -> pd.DataFrame:
        """Generate the synthetic credit dataset as a Pandas DataFrame."""
        rows = self.config.rows
        rng = np.random.default_rng(self.config.seed)

        employment_type = rng.choice(
            np.array(EMPLOYMENT_TYPES),
            size=rows,
            p=EMPLOYMENT_PROBABILITIES,
        )
        employment_series = pd.Series(employment_type)

        age = self._generate_age(employment_type, rng)

        employment_stability = (
            employment_series.map(EMPLOYMENT_STABILITY)
            .to_numpy(dtype=float)
        )

        unemployed_flag = (
            (employment_series == "unemployed")
            .astype(np.int8)
            .to_numpy()
        )

        base_log_income = (
            employment_series.map(EMPLOYMENT_INCOME_LOG_BASE)
            .to_numpy(dtype=float)
        )

        monthly_income = np.exp(
            base_log_income + rng.normal(0.0, 0.38, size=rows)
        ).round(2)

        age_factor = (age - 21) / (70 - 21)

        # A hidden behavioral score used only to generate realistic features.
        # This latent variable is intentionally not saved in the final dataset
        # to avoid target leakage in the machine learning phase.
        financial_discipline_latent = (
            0.58 * employment_stability
            + 0.22 * age_factor
            + rng.normal(0.0, 0.30, size=rows)
        )

        financial_discipline_latent = (
            financial_discipline_latent - financial_discipline_latent.mean()
        ) / (financial_discipline_latent.std() + 1e-8)

        rent_payment_on_time_rate = self._bounded_rate(
            rng=rng,
            latent=financial_discipline_latent,
            offset=0.35,
            noise_scale=0.40,
        )

        utility_payment_on_time_rate = self._bounded_rate(
            rng=rng,
            latent=financial_discipline_latent,
            offset=0.45,
            noise_scale=0.35,
        )

        telecom_payment_on_time_rate = self._bounded_rate(
            rng=rng,
            latent=financial_discipline_latent,
            offset=0.50,
            noise_scale=0.30,
        )

        # Some customers do not have rent history.
        # This creates meaningful missingness, not random noise.
        has_rent_history = rng.random(rows) < 0.88
        rent_payment_on_time_rate = np.where(
            has_rent_history,
            rent_payment_on_time_rate,
            np.nan,
        )

        monthly_avg_telco_charge = np.clip(
            monthly_income * rng.uniform(0.012, 0.045, size=rows),
            5.0,
            None,
        ).round(2)

        savings_behavior_score = np.clip(
            55.0
            + 18.0 * financial_discipline_latent
            + rng.normal(0.0, 9.0, size=rows),
            0.0,
            100.0,
        ).round(2)

        ecommerce_activity_score = np.clip(
            42.0
            + 0.015 * monthly_income
            + 8.0 * age_factor
            + rng.normal(0.0, 12.0, size=rows),
            0.0,
            100.0,
        ).round(2)

        digital_wallet_usage_score = np.clip(
            62.0
            - 0.35 * (age - 38)
            + rng.normal(0.0, 12.0, size=rows),
            0.0,
            100.0,
        ).round(2)

        months_at_current_address = self._generate_months_at_current_address(
            age,
            rng,
        )

        number_of_dependents = self._generate_number_of_dependents(
            age,
            rng,
        )

        # Synthetic default risk target.
        # In a real bank, this would be observed after 12 months.
        default_logit = (
            -1.35
            - 1.25 * financial_discipline_latent
            + 0.75 * unemployed_flag
            + 0.18 * (number_of_dependents / 6.0)
            - 0.004 * savings_behavior_score
            + rng.normal(0.0, 0.35, size=rows)
        )

        default_probability = self._sigmoid(default_logit)
        is_default_12m = rng.binomial(1, default_probability).astype(np.int8)

        customer_ids = [f"CW-{idx:06d}" for idx in range(rows)]
        customer_names = [self.faker.name() for _ in range(rows)]

        df = pd.DataFrame(
            {
                "customer_id": customer_ids,
                "customer_name": customer_names,
                "age": age,
                "employment_type": employment_type,
                "monthly_income": monthly_income,
                "months_at_current_address": months_at_current_address,
                "number_of_dependents": number_of_dependents,
                "has_rent_history": has_rent_history.astype(np.int8),
                "rent_payment_on_time_rate": rent_payment_on_time_rate,
                "utility_payment_on_time_rate": utility_payment_on_time_rate,
                "telecom_payment_on_time_rate": telecom_payment_on_time_rate,
                "monthly_avg_telco_charge": monthly_avg_telco_charge,
                "ecommerce_activity_score": ecommerce_activity_score,
                "digital_wallet_usage_score": digital_wallet_usage_score,
                "savings_behavior_score": savings_behavior_score,
                "is_default_12m": is_default_12m,
            }
        )

        return self._post_process(df)

    @staticmethod
    def _generate_age(
        employment_type: np.ndarray,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Generate realistic ages based on employment type."""
        retired_mask = employment_type == "retired"
        age = np.empty(employment_type.shape[0], dtype=np.int64)

        retired_count = int(retired_mask.sum())
        non_retired_count = int((~retired_mask).sum())

        if retired_count > 0:
            age[retired_mask] = rng.integers(55, 71, size=retired_count)

        if non_retired_count > 0:
            age[~retired_mask] = rng.integers(21, 66, size=non_retired_count)

        return age

    @staticmethod
    def _generate_months_at_current_address(
        age: np.ndarray,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Generate months at current address correlated with age."""
        max_possible_months = np.clip((age - 18) * 12, 6, 360)
        max_allowed_months = np.minimum(max_possible_months, 240)

        months = (
            rng.random(age.shape[0]) * max_allowed_months
        ).astype(np.int64) + 1

        return months

    @staticmethod
    def _generate_number_of_dependents(
        age: np.ndarray,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Generate number of dependents correlated with age."""
        base = np.clip(
            (age - 21) / 49.0 * 3.5 + rng.normal(0.0, 0.9, age.shape[0]),
            0.0,
            6.0,
        )
        return np.floor(base).astype(np.int8)

    @staticmethod
    def _bounded_rate(
        rng: np.random.Generator,
        latent: np.ndarray,
        offset: float,
        noise_scale: float,
    ) -> np.ndarray:
        """Generate a bounded payment behavior rate between 0.02 and 0.99."""
        raw = offset + latent + rng.normal(0.0, noise_scale, size=latent.shape)
        rate = 1.0 / (1.0 + np.exp(-raw))
        return np.clip(rate, 0.02, 0.99)

    @staticmethod
    def _sigmoid(values: np.ndarray) -> np.ndarray:
        """Numerically simple sigmoid for binary target generation."""
        return 1.0 / (1.0 + np.exp(-values))

    @staticmethod
    def _post_process(df: pd.DataFrame) -> pd.DataFrame:
        """Apply final formatting and rounding."""
        float_columns = df.select_dtypes(include="float").columns
        df[float_columns] = df[float_columns].round(4)
        return df


def save_dataset(df: pd.DataFrame, output_path: Path) -> None:
    """Save generated dataset to CSV and log basic quality metrics."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    default_rate = df["is_default_12m"].mean()

    logger.info("Dataset saved at: %s", output_path)
    logger.info("Shape: %s rows, %s columns", df.shape[0], df.shape[1])
    logger.info("Default rate: %.2f%%", default_rate * 100)
    logger.info("Missing values per column:\n%s", df.isna().sum().to_string())


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a synthetic alternative-data credit dataset for CreditWise."
    )

    parser.add_argument(
        "--rows",
        type=int,
        default=10_000,
        help="Number of synthetic customers to generate.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible dataset generation.",
    )

    parser.add_argument(
        "--locale",
        type=str,
        default="fa_IR",
        help="Faker locale for synthetic customer names.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output CSV file path.",
    )

    return parser.parse_args()


def main() -> None:
    """Entry point for synthetic data generation."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    args = parse_args()

    try:
        config = GenerationConfig(
            rows=args.rows,
            seed=args.seed,
            locale=args.locale,
        )
        config.validate()

        generator = SyntheticCreditDatasetGenerator(config=config)
        df = generator.generate()

        save_dataset(df=df, output_path=args.output)

    except Exception as exc:
        logger.error("Synthetic data generation failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()