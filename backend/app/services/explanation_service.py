from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.config import (
    EXPLANATION_LANGUAGE,
    EXPLANATION_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
)
from app.schemas.credit import (
    CreditApplicationRequest,
    CreditScoreResponse,
)
from app.schemas.explanation import (
    CreditExplanationResponse,
    ExplanationFactor,
    ExplanationProvider,
    FactorDirection,
)

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore


FEATURE_TITLES: dict[str, str] = {
    "utility_payment_on_time_rate": "پرداخت به‌موقع قبوض",
    "telecom_payment_on_time_rate": "پرداخت به‌موقع موبایل",
    "rent_payment_on_time_rate": "پرداخت به‌موقع اجاره",
    "savings_behavior_score": "رفتار پس‌انداز",
    "employment_type": "وضعیت اشتغال",
    "monthly_income": "درآمد ماهانه",
    "months_at_current_address": "ثبات سکونت",
    "number_of_dependents": "تعداد وابستگان",
}

RISK_LABELS: dict[str, str] = {
    "low": "کم",
    "medium": "متوسط",
    "high": "زیاد",
}

DECISION_LABELS: dict[str, str] = {
    "approve": "تأیید اولیه",
    "review": "بررسی تکمیلی",
    "decline": "عدم تأیید اولیه",
}


class ExplanationService:
    """Generates human-friendly explanations for credit decisions."""

    def __init__(self) -> None:
        self.provider: ExplanationProvider = self._normalize_provider(
            EXPLANATION_PROVIDER
        )
        self.openai_client: Optional[Any] = None

        if self.provider == "openai":
            self._initialize_openai_client()

    @staticmethod
    def _normalize_provider(provider: str) -> ExplanationProvider:
        """Normalize explanation provider name."""
        provider = provider.strip().lower()

        if provider == "openai":
            return "openai"

        return "local"

    def _initialize_openai_client(self) -> None:
        """Initialize an OpenAI-compatible client (cloud or local LLM)."""
        if OpenAI is None:
            logger.warning(
                "openai package is not installed. "
                "Falling back to local explanation provider."
            )
            self.provider = "local"
            return

        # Local/self-hosted LLM servers usually do not require a real API key,
        # but the official OpenAI client rejects an empty string.
        # Therefore we fall back to a dummy key for local endpoints.
        api_key = OPENAI_API_KEY or "not-needed-for-local-llm"

        base_url = OPENAI_BASE_URL or None

        try:
            self.openai_client = OpenAI(
                api_key=api_key,
                base_url=base_url,
            )
        except Exception as exc:
            logger.warning(
                "Failed to initialize OpenAI-compatible client (base_url=%s): %s. "
                "Falling back to local explanation provider.",
                base_url,
                exc,
            )
            self.provider = "local"
            return

        logger.info(
            "OpenAI-compatible provider initialized. base_url=%s model=%s",
            base_url,
            OPENAI_MODEL,
        )

    def explain(
        self,
        application: CreditApplicationRequest,
        score_response: CreditScoreResponse,
    ) -> CreditExplanationResponse:
        """Generate an explanation for a scored credit application."""
        factors = self._build_factors(application)
        recommendations = self._build_recommendations(application)

        if self.provider == "openai" and self.openai_client is not None:
            try:
                texts = self._generate_with_openai(
                    application=application,
                    score_response=score_response,
                    factors=factors,
                )
                generated_by: ExplanationProvider = "openai"
            except Exception:
                logger.exception(
                    "OpenAI explanation generation failed. "
                    "Falling back to local explanation."
                )
                texts = self._generate_local_texts(
                    application=application,
                    score_response=score_response,
                    factors=factors,
                )
                generated_by = "local"
        else:
            texts = self._generate_local_texts(
                application=application,
                score_response=score_response,
                factors=factors,
            )
            generated_by = "local"

        return CreditExplanationResponse(
            request_id=score_response.request_id,
            credit_score=score_response.credit_score,
            default_probability=score_response.default_probability,
            risk_level=score_response.risk_level,
            decision=score_response.decision,
            summary=texts["summary"],
            customer_message=texts["customer_message"],
            employee_note=texts["employee_note"],
            factors=factors,
            recommendations=recommendations,
            generated_by=generated_by,
            timestamp=datetime.now(timezone.utc),
        )

    def _build_factors(
        self,
        application: CreditApplicationRequest,
    ) -> list[ExplanationFactor]:
        """Build structured explanation factors from application data."""
        factors: list[ExplanationFactor] = []

        self._add_payment_factor(
            factors=factors,
            feature="utility_payment_on_time_rate",
            value=application.utility_payment_on_time_rate,
        )

        self._add_payment_factor(
            factors=factors,
            feature="telecom_payment_on_time_rate",
            value=application.telecom_payment_on_time_rate,
        )

        self._add_rent_factor(factors, application)

        self._add_savings_factor(
            factors=factors,
            value=application.savings_behavior_score,
        )

        self._add_employment_factor(
            factors=factors,
            employment_type=application.employment_type,
        )

        self._add_income_factor(
            factors=factors,
            income=application.monthly_income,
        )

        self._add_address_factor(
            factors=factors,
            months_at_current_address=application.months_at_current_address,
        )

        self._add_dependents_factor(
            factors=factors,
            application=application,
        )

        return factors[:6]

    @staticmethod
    def _create_factor(
        feature: str,
        direction: FactorDirection,
        description: str,
    ) -> ExplanationFactor:
        """Create an explanation factor object."""
        return ExplanationFactor(
            feature=feature,
            title=FEATURE_TITLES.get(feature, feature),
            direction=direction,
            description=description,
        )

    def _add_payment_factor(
        self,
        factors: list[ExplanationFactor],
        feature: str,
        value: float,
    ) -> None:
        """Add a payment-history factor."""
        percent = int(round(value * 100))

        if value >= 0.90:
            direction: FactorDirection = "positive"
            description = (
                f"نسبت پرداخت به‌موقع {percent}٪ است "
                "و نشانه قوی از نظم مالی محسوب می‌شود."
            )
        elif value >= 0.75:
            direction = "positive"
            description = (
                f"نسبت پرداخت به‌موقع {percent}٪ است "
                "و به‌عنوان رفتار نسبتاً مناسب ارزیابی می‌شود."
            )
        elif value <= 0.60:
            direction = "negative"
            description = (
                f"نسبت پرداخت به‌موقع {percent}٪ است "
                "و ممکن است نشانه‌ای از تأخیر در پرداخت‌ها باشد."
            )
        else:
            direction = "neutral"
            description = (
                f"نسبت پرداخت به‌موقع {percent}٪ است "
                "و در محدوده متوسط قرار دارد."
            )

        factors.append(self._create_factor(feature, direction, description))

    def _add_rent_factor(
        self,
        factors: list[ExplanationFactor],
        application: CreditApplicationRequest,
    ) -> None:
        """Add rent payment history factor."""
        feature = "rent_payment_on_time_rate"

        if not application.has_rent_history:
            factors.append(
                self._create_factor(
                    feature=feature,
                    direction="neutral",
                    description=(
                        "سابقه پرداخت اجاره ثبت نشده است. "
                        "این موضوع لزوماً منفی نیست، اما ارزیابی "
                        "سابقه اجاره را محدود می‌کند."
                    ),
                )
            )
            return

        value = application.rent_payment_on_time_rate

        if value is None:
            factors.append(
                self._create_factor(
                    feature=feature,
                    direction="neutral",
                    description=(
                        "سابقه اجاره وجود دارد، اما داده کافی برای "
                        "نرخ پرداخت به‌موقع ثبت نشده است."
                    ),
                )
            )
            return

        percent = int(round(value * 100))

        if value >= 0.85:
            direction: FactorDirection = "positive"
            description = (
                f"نسبت پرداخت به‌موقع اجاره {percent}٪ است "
                "و نشانه مناسبی از پایبندی به تعهدات مالی است."
            )
        elif value <= 0.60:
            direction = "negative"
            description = (
                f"نسبت پرداخت به‌موقع اجاره {percent}٪ است "
                "و ممکن است نشانه‌ای از تأخیر در پرداخت اجاره باشد."
            )
        else:
            direction = "neutral"
            description = (
                f"نسبت پرداخت به‌موقع اجاره {percent}٪ است "
                "و در محدوده متوسط ارزیابی می‌شود."
            )

        factors.append(self._create_factor(feature, direction, description))

    def _add_savings_factor(
        self,
        factors: list[ExplanationFactor],
        value: float,
    ) -> None:
        """Add savings behavior factor."""
        feature = "savings_behavior_score"

        if value >= 65:
            direction: FactorDirection = "positive"
            description = (
                "رفتار پس‌انداز در سطح مناسبی قرار دارد و می‌تواند "
                "نشانه‌ای از ثبات مالی باشد."
            )
        elif value <= 35:
            direction = "negative"
            description = (
                "رفتار پس‌انداز در سطح پایینی قرار دارد و ممکن است "
                "تاب‌آوری مالی را محدود کند."
            )
        else:
            direction = "neutral"
            description = "رفتار پس‌انداز در محدوده متوسط ارزیابی می‌شود."

        factors.append(self._create_factor(feature, direction, description))

    def _add_employment_factor(
        self,
        factors: list[ExplanationFactor],
        employment_type: str,
    ) -> None:
        """Add employment stability factor."""
        feature = "employment_type"

        if employment_type in {"salaried", "retired"}:
            direction: FactorDirection = "positive"
            description = (
                "وضعیت اشتغال ثبت‌شده نسبتاً پایدار است و می‌تواند "
                "به پیش‌بینی‌پذیرتر بودن جریان درآمدی کمک کند."
            )
        elif employment_type == "unemployed":
            direction = "negative"
            description = (
                "وضعیت اشتغال فعلی ممکن است توان بازپرداخت را "
                "با عدم قطعیت بیشتری مواجه کند."
            )
        elif employment_type == "gig":
            direction = "negative"
            description = (
                "درآمد مبتنی بر پروژه یا کار موردی ممکن است متغیر باشد "
                "و نیازمند بررسی بیشتر جریان درآمد است."
            )
        else:
            direction = "neutral"
            description = (
                "وضعیت اشتغال ثبت‌شده در محدوده متوسط ارزیابی می‌شود "
                "و ممکن است نیازمند تأیید مدارک درآمدی باشد."
            )

        factors.append(self._create_factor(feature, direction, description))

    def _add_income_factor(
        self,
        factors: list[ExplanationFactor],
        income: float,
    ) -> None:
        """Add income factor."""
        feature = "monthly_income"

        if income >= 1000:
            direction: FactorDirection = "positive"
            description = (
                "درآمد ثبت‌شده در سطح نسبتاً مناسبی قرار دارد."
            )
        elif income <= 450:
            direction = "negative"
            description = (
                "درآمد ثبت‌شده ممکن است توان بازپرداخت را محدود کند."
            )
        else:
            direction = "neutral"
            description = "درآمد ثبت‌شده در محدوده متوسط ارزیابی می‌شود."

        factors.append(self._create_factor(feature, direction, description))

    def _add_address_factor(
        self,
        factors: list[ExplanationFactor],
        months_at_current_address: int,
    ) -> None:
        """Add residential stability factor."""
        feature = "months_at_current_address"

        if months_at_current_address >= 24:
            direction: FactorDirection = "positive"
            description = (
                "مدت سکونت در آدرس فعلی نسبتاً بالاست و می‌تواند "
                "نشانه‌ای از ثبات فردی باشد."
            )
        elif months_at_current_address <= 6:
            direction = "negative"
            description = (
                "مدت سکونت در آدرس فعلی کوتاه است و ممکن است "
                "نیازمند اطلاعات تکمیلی باشد."
            )
        else:
            direction = "neutral"
            description = "مدت سکونت در آدرس فعلی در محدوده متوسط است."

        factors.append(self._create_factor(feature, direction, description))

    def _add_dependents_factor(
        self,
        factors: list[ExplanationFactor],
        application: CreditApplicationRequest,
    ) -> None:
        """Add dependents pressure factor."""
        feature = "number_of_dependents"

        if application.number_of_dependents >= 4 and application.monthly_income < 800:
            direction: FactorDirection = "negative"
            description = (
                "نسبت تعداد وابستگان به درآمد ثبت‌شده ممکن است "
                "فشار مالی را افزایش دهد."
            )
        elif application.number_of_dependents <= 1:
            direction = "neutral"
            description = "تعداد وابستگان کم است."
        else:
            direction = "neutral"
            description = "تعداد وابستگان در محدوده متوسط ارزیابی می‌شود."

        factors.append(self._create_factor(feature, direction, description))

    def _build_recommendations(
        self,
        application: CreditApplicationRequest,
    ) -> list[str]:
        """Build practical recommendations based on application data."""
        recommendations: list[str] = []

        if (
            application.utility_payment_on_time_rate <= 0.70
            or application.telecom_payment_on_time_rate <= 0.70
        ):
            recommendations.append(
                "پرداخت به‌موقع قبوض و هزینه‌های موبایل می‌تواند "
                "سابقه اعتباری را به‌مرور بهبود دهد."
            )

        if not application.has_rent_history:
            recommendations.append(
                "در صورت امکان، ثبت قرارداد اجاره و انجام پرداخت‌ها "
                "از طریق کانال‌های بانکی به ایجاد سابقه کمک می‌کند."
            )

        if application.savings_behavior_score <= 40:
            recommendations.append(
                "برنامه پس‌انداز منظم، حتی با مبالغ کوچک، می‌تواند "
                "نشانه مثبتی از رفتار مالی باشد."
            )

        if (
            application.employment_type in {"unemployed", "gig"}
            or application.monthly_income <= 500
        ):
            recommendations.append(
                "ارائه مدارک درآمدی تکمیلی یا تضمین مناسب می‌تواند "
                "شانس تأیید درخواست را افزایش دهد."
            )

        if application.number_of_dependents >= 4 and application.monthly_income < 800:
            recommendations.append(
                "بازبینی مبلغ درخواستی یا افزایش بازه بازپرداخت "
                "می‌تواند فشار مالی را کاهش دهد."
            )

        if not recommendations:
            recommendations.append(
                "ادامه رفتار مالی فعلی و حفظ پرداخت‌های منظم "
                "می‌تواند به بهبود امتیاز اعتباری کمک کند."
            )

        return recommendations[:4]

    def _generate_local_texts(
        self,
        application: CreditApplicationRequest,
        score_response: CreditScoreResponse,
        factors: list[ExplanationFactor],
    ) -> dict[str, str]:
        """Generate deterministic local explanation texts."""
        risk_label = RISK_LABELS[score_response.risk_level]
        decision_label = DECISION_LABELS[score_response.decision]

        summary = (
            f"نتیجه ارزیابی اولیه: {decision_label}؛ "
            f"امتیاز اعتباری {score_response.credit_score} "
            f"و سطح ریسک {risk_label} برآورد شده است."
        )

        positive_titles = [
            factor.title
            for factor in factors
            if factor.direction == "positive"
        ][:2]

        negative_titles = [
            factor.title
            for factor in factors
            if factor.direction == "negative"
        ][:2]

        positive_text = (
            "، ".join(positive_titles)
            if positive_titles
            else "برخی رفتارهای مالی مشتری نیاز به بررسی بیشتر دارد"
        )

        negative_text = (
            "، ".join(negative_titles)
            if negative_titles
            else "عامل منفی شدیدی در داده‌های ثبت‌شده مشاهده نشد"
        )

        if score_response.decision == "approve":
            customer_message = (
                "نتیجه اولیه بررسی درخواست شما مثبت است. "
                f"نقاط قوتی مانند {positive_text} در ارزیابی مؤثر بوده‌اند. "
                "تصمیم نهایی پس از تکمیل فرآیندهای بانکی اعلام خواهد شد."
            )
        elif score_response.decision == "review":
            customer_message = (
                "درخواست شما نیازمند بررسی تکمیلی است. "
                f"مواردی مانند {negative_text} باعث شد نتیجه فعلی "
                "در حالت بررسی قرار بگیرد. در صورت نیاز، مدارک تکمیلی "
                "از طریق کانال رسمی بانک اعلام می‌شود."
            )
        else:
            customer_message = (
                "بر اساس داده‌های موجود، امکان تأیید اولیه در این مرحله "
                "فراهم نشد. "
                f"عواملی مانند {negative_text} در این نتیجه مؤثر بوده‌اند. "
                "با بهبود برخی رفتارهای مالی یا ارائه مدارک تکمیلی، "
                "می‌توان درخواست جدیدی ثبت کرد."
            )

        employee_note = (
            f"درخواست با امتیاز {score_response.credit_score} "
            f"و احتمال نکول {score_response.default_probability:.2%} ارزیابی شد. "
            f"عوامل مثبت: {positive_text}. "
            f"عوامل نیازمند توجه: {negative_text}. "
            f"پیشنهاد عملیاتی: {decision_label}."
        )

        return {
            "summary": summary,
            "customer_message": customer_message,
            "employee_note": employee_note,
        }

    def _generate_with_openai(
        self,
        application: CreditApplicationRequest,
        score_response: CreditScoreResponse,
        factors: list[ExplanationFactor],
    ) -> dict[str, str]:
        """Generate explanation texts using OpenAI API."""
        payload: dict[str, Any] = {
            "language": EXPLANATION_LANGUAGE or "fa",
            "credit_score": score_response.credit_score,
            "default_probability": score_response.default_probability,
            "risk_level": score_response.risk_level,
            "decision": score_response.decision,
            "application": application.model_dump(exclude={"customer_id"}),
            "factors": [factor.model_dump() for factor in factors],
        }

        system_prompt = (
            "You are a bank credit explanation generator.\n\n"
            "TASK: Convert credit scoring results into Persian (Farsi) explanations.\n\n"
            "OUTPUT FORMAT: Return ONLY a valid JSON object with exactly these 3 keys:\n"
            "- summary (string, max 80 chars): Short evaluation result\n"
            "- customer_message (string): Respectful message for customer in Persian\n"
            "- employee_note (string): Operational note for bank employee in Persian\n\n"
            "RULES:\n"
            "1. All values MUST be in Persian (Farsi) language.\n"
            "2. Do NOT add any text before or after the JSON.\n"
            "3. Do NOT use markdown code fences (```json).\n"
            "4. Do NOT explain your reasoning. Just output the JSON.\n"
            "5. Be respectful, transparent, and non-technical for customers.\n"
            "6. Be analytical and operational for employees.\n"
            "7. Do NOT mention race, gender, ethnicity, or religion.\n"
            "8. Do NOT promise final approval. Use 'initial result' or 'preliminary'.\n\n"
            "EXAMPLE OUTPUT:\n"
            "{\n"
            '  "summary": "نتیجه ارزیابی اولیه: تأیید درخواست.",\n'
            '  "customer_message": "درخواست شما بررسی شد و نتیجه اولیه مثبت است. نقاط قوت شما شامل پرداخت منظم قبوض و سابقه خوب اجاره است.",\n'
            '  "employee_note": "درخواست با امتیاز 750 و ریسک پایین ارزیابی شد. پیشنهاد: تأیید اولیه."\n'
            "}\n\n"
            "Now generate the JSON for the given input. Output ONLY the JSON object, nothing else."
        )

        user_prompt = (
            "Generate Persian explanations for this credit decision.\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
        )

        completion = self.openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.2,
            max_tokens=800,
            timeout=60.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = completion.choices[0].message.content or ""

        # Log the raw response for debugging
        logger.info("Raw LLM response content: %s", repr(content[:500]) if content else "EMPTY")
        logger.info("Full message object: %s", completion.choices[0].message)

        parsed = self._extract_json(content)

        required_keys = {"summary", "customer_message", "employee_note"}

        if not required_keys.issubset(parsed.keys()):
            raise ValueError("OpenAI response did not contain required keys.")

        return {
            "summary": str(parsed["summary"]).strip(),
            "customer_message": str(parsed["customer_message"]).strip(),
            "employee_note": str(parsed["employee_note"]).strip(),
        }


    @staticmethod
    def _extract_json(content: str) -> dict[str, Any]:
        """Extract JSON object from LLM response robustly.

        Handles:
        - Raw JSON: {...}
        - Markdown-fenced: ```json\n{...}\n```
        - JSON embedded in text: "Here is the JSON: {...}"
        - Multiple JSON objects (takes the first valid one)
        """
        if not content or not content.strip():
            raise ValueError(
                "LLM returned empty content. "
                "Check if the model is a reasoning model."
            )

        content = content.strip()

        # Strip markdown code fences
        if "```" in content:
            content = content.replace("```json", "").replace("```JSON", "").replace("```", "")

        # Try to find JSON objects in the content
        json_objects = []
        start = 0
        
        while True:
            obj_start = content.find("{", start)
            if obj_start == -1:
                break
            
            # Find matching closing brace
            brace_count = 0
            obj_end = obj_start
            
            for i in range(obj_start, len(content)):
                if content[i] == "{":
                    brace_count += 1
                elif content[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        obj_end = i + 1
                        break
            
            if obj_end > obj_start:
                json_text = content[obj_start:obj_end]
                try:
                    parsed = json.loads(json_text)
                    json_objects.append(parsed)
                except json.JSONDecodeError:
                    pass  # Invalid JSON, continue searching
            
            start = obj_end
        
        if not json_objects:
            raise ValueError(
                f"No valid JSON object found in model response. "
                f"Received (first 500 chars): {content[:500]}"
            )
        
        # Return the first valid JSON object
        return json_objects[0]


    def _generate_with_openai(
        self,
        application: CreditApplicationRequest,
        score_response: CreditScoreResponse,
        factors: list[ExplanationFactor],
    ) -> dict[str, str]:
        """Generate explanation texts using OpenAI-compatible API."""
        payload: dict[str, Any] = {
            "language": EXPLANATION_LANGUAGE or "fa",
            "credit_score": score_response.credit_score,
            "default_probability": score_response.default_probability,
            "risk_level": score_response.risk_level,
            "decision": score_response.decision,
            "application": application.model_dump(exclude={"customer_id"}),
            "factors": [factor.model_dump() for factor in factors],
        }

        system_prompt = (
            "You are a respectful explanation writer for a bank credit system. "
            "Your task is to convert structured credit scoring results into "
            "plain, respectful, transparent Persian explanations. "
            "Do not mention race, gender, ethnicity, religion, or other sensitive attributes. "
            "Do not provide legal, investment, or financial advice. "
            "Do not promise final bank approval. "
            "Return ONLY valid JSON with these keys: "
            "summary, customer_message, employee_note."
        )

        user_prompt = (
            "Generate Persian explanations for this credit decision.\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
        )

        # Try with response_format first
        try:
            completion = self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.4,  # Increased from 0.2 to avoid reasoning loops
                max_tokens=1500,  # Increased from 800 for reasoning + JSON
                timeout=60.0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as format_exc:
            logger.warning(
                "response_format not supported (%s). Retrying without it.",
                format_exc,
            )
            completion = self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.4,
                max_tokens=1500,
                timeout=60.0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

        message = completion.choices[0].message
        
        # Try to extract content from various fields (handles reasoning models)
        content = (
            getattr(message, "content", None)
            or getattr(message, "reasoning_content", None)
            or getattr(message, "reasoning", None)
            or getattr(message, "text", None)
            or ""
        )
        
        # Log the raw response for debugging
        logger.info("Raw LLM response content: %s", repr(content[:500]) if content else "EMPTY")
        logger.info("Full message object keys: %s", list(message.model_dump().keys()))

        parsed = self._extract_json(content)

        required_keys = {"summary", "customer_message", "employee_note"}

        if not required_keys.issubset(parsed.keys()):
            raise ValueError(
                f"OpenAI response did not contain required keys. "
                f"Found keys: {list(parsed.keys())}. "
                f"Required: {required_keys}"
            )

        return {
            "summary": str(parsed["summary"]).strip(),
            "customer_message": str(parsed["customer_message"]).strip(),
            "employee_note": str(parsed["employee_note"]).strip(),
        }