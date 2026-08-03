export type EmploymentType =
  | "salaried"
  | "self_employed"
  | "contract"
  | "gig"
  | "retired"
  | "unemployed";

export type RiskLevel = "low" | "medium" | "high";
export type Decision = "approve" | "review" | "decline";
export type FactorDirection = "positive" | "negative" | "neutral";
export type ExplanationProvider = "local" | "openai";

export interface CreditApplicationRequest {
  customer_id?: string;
  age: number;
  employment_type: EmploymentType;
  monthly_income: number;
  months_at_current_address: number;
  number_of_dependents: number;
  has_rent_history: boolean;
  rent_payment_on_time_rate: number | null;
  utility_payment_on_time_rate: number;
  telecom_payment_on_time_rate: number;
  monthly_avg_telco_charge: number;
  ecommerce_activity_score: number;
  digital_wallet_usage_score: number;
  savings_behavior_score: number;
}

export interface FeatureFactor {
  feature: string;
  title: string;
  direction: FactorDirection;
  description: string;
}

export interface CreditExplanationResponse {
  request_id: string;
  credit_score: number;
  default_probability: number;
  risk_level: RiskLevel;
  decision: Decision;
  summary: string;
  customer_message: string;
  employee_note: string;
  factors: FeatureFactor[];
  recommendations: string[];
  generated_by: ExplanationProvider;
  timestamp: string;
}