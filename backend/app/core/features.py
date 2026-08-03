from typing import Final

EMPLOYMENT_TYPES: Final[tuple[str, ...]] = (
    "salaried",
    "self_employed",
    "contract",
    "gig",
    "retired",
    "unemployed",
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

CATEGORICAL_FEATURES: Final[tuple[str, ...]] = (
    "employment_type",
)

FEATURE_COLUMNS: Final[tuple[str, ...]] = (
    NUMERIC_FEATURES + CATEGORICAL_FEATURES
)