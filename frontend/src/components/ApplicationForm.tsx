import { useState, type FormEvent } from "react";
import type { CreditApplicationRequest, EmploymentType } from "../types/credit";

interface ApplicationFormProps {
  onSubmit: (application: CreditApplicationRequest) => void;
  isLoading: boolean;
}

const EMPLOYMENT_OPTIONS: { value: EmploymentType; label: string }[] = [
  { value: "salaried", label: "کارمند (حقوق‌بگیر)" },
  { value: "self_employed", label: "خویش‌فرما" },
  { value: "contract", label: "قراردادی" },
  { value: "gig", label: "کار موردی/پروژه‌ای" },
  { value: "retired", label: "بازنشسته" },
  { value: "unemployed", label: "بیکار" },
];

export function ApplicationForm({ onSubmit, isLoading }: ApplicationFormProps) {
  const [formData, setFormData] = useState<CreditApplicationRequest>({
    age: 35,
    employment_type: "salaried",
    monthly_income: 1200,
    months_at_current_address: 36,
    number_of_dependents: 1,
    has_rent_history: true,
    rent_payment_on_time_rate: 0.89,
    utility_payment_on_time_rate: 0.95,
    telecom_payment_on_time_rate: 0.87,
    monthly_avg_telco_charge: 32.5,
    ecommerce_activity_score: 61,
    digital_wallet_usage_score: 72,
    savings_behavior_score: 66,
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const updateField = <K extends keyof CreditApplicationRequest>(
    field: K,
    value: CreditApplicationRequest[K]
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const loadSample = (type: "good" | "bad") => {
    if (type === "good") {
      setFormData({
        age: 34,
        employment_type: "salaried",
        monthly_income: 1200,
        months_at_current_address: 36,
        number_of_dependents: 1,
        has_rent_history: true,
        rent_payment_on_time_rate: 0.89,
        utility_payment_on_time_rate: 0.95,
        telecom_payment_on_time_rate: 0.87,
        monthly_avg_telco_charge: 32.5,
        ecommerce_activity_score: 61,
        digital_wallet_usage_score: 72,
        savings_behavior_score: 66,
      });
    } else {
      setFormData({
        age: 24,
        employment_type: "gig",
        monthly_income: 350,
        months_at_current_address: 5,
        number_of_dependents: 3,
        has_rent_history: false,
        rent_payment_on_time_rate: null,
        utility_payment_on_time_rate: 0.52,
        telecom_payment_on_time_rate: 0.48,
        monthly_avg_telco_charge: 11.2,
        ecommerce_activity_score: 22,
        digital_wallet_usage_score: 65,
        savings_behavior_score: 18,
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      <div className="mb-6 flex flex-col sm:flex-row gap-3 sm:justify-between sm:items-center">
        <div>
          <h2 className="text-xl font-bold text-bank-primary">
            فرم درخواست اعتبار
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            اطلاعات جایگزین مشتری را برای ارزیابی وارد کنید
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => loadSample("good")}
            className="text-xs px-3 py-2 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors"
          >
            نمونه مشتری خوب
          </button>
          <button
            type="button"
            onClick={() => loadSample("bad")}
            className="text-xs px-3 py-2 bg-red-50 text-red-700 rounded-md hover:bg-red-100 transition-colors"
          >
            نمونه مشتری پرریسک
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* اطلاعات پایه */}
        <div className="md:col-span-2 lg:col-span-3">
          <h3 className="text-sm font-semibold text-slate-600 mb-3 border-b border-slate-200 pb-2">
            اطلاعات پایه
          </h3>
        </div>

        <div>
          <label className="label">سن</label>
          <input
            type="number"
            className="input-field"
            value={formData.age}
            onChange={(e) => updateField("age", Number(e.target.value))}
            min={18}
            max={100}
          />
        </div>

        <div>
          <label className="label">وضعیت اشتغال</label>
          <select
            className="input-field"
            value={formData.employment_type}
            onChange={(e) =>
              updateField("employment_type", e.target.value as EmploymentType)
            }
          >
            {EMPLOYMENT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="label">درآمد ماهانه</label>
          <input
            type="number"
            className="input-field"
            value={formData.monthly_income}
            onChange={(e) =>
              updateField("monthly_income", Number(e.target.value))
            }
            min={0}
            step={50}
          />
        </div>

        {/* ثبات سکونت و وابستگان */}
        <div>
          <label className="label">مدت سکونت در آدرس فعلی (ماه)</label>
          <input
            type="number"
            className="input-field"
            value={formData.months_at_current_address}
            onChange={(e) =>
              updateField("months_at_current_address", Number(e.target.value))
            }
            min={0}
            max={600}
          />
        </div>

        <div>
          <label className="label">تعداد افراد تحت تکفل</label>
          <input
            type="number"
            className="input-field"
            value={formData.number_of_dependents}
            onChange={(e) =>
              updateField("number_of_dependents", Number(e.target.value))
            }
            min={0}
            max={20}
          />
        </div>

        {/* سابقه پرداخت */}
        <div className="md:col-span-2 lg:col-span-3 mt-4">
          <h3 className="text-sm font-semibold text-slate-600 mb-3 border-b border-slate-200 pb-2">
            سابقه پرداخت
          </h3>
        </div>

        <div className="flex items-center gap-3 md:col-span-2 lg:col-span-3">
          <input
            type="checkbox"
            id="has_rent_history"
            checked={formData.has_rent_history}
            onChange={(e) =>
              updateField("has_rent_history", e.target.checked)
            }
            className="w-5 h-5 text-bank-primary rounded"
          />
          <label htmlFor="has_rent_history" className="text-sm text-slate-700">
            دارای سابقه پرداخت اجاره
          </label>
        </div>

        <div>
          <label className="label">
            پرداخت به‌موقع اجاره
            <span className="text-xs text-slate-400 mr-1">(0 تا 1)</span>
          </label>
          <input
            type="number"
            step="0.01"
            className="input-field"
            value={formData.rent_payment_on_time_rate ?? 0}
            onChange={(e) =>
              updateField("rent_payment_on_time_rate", Number(e.target.value))
            }
            min={0}
            max={1}
            disabled={!formData.has_rent_history}
          />
        </div>

        <div>
          <label className="label">
            پرداخت به‌موقع قبوض
            <span className="text-xs text-slate-400 mr-1">(0 تا 1)</span>
          </label>
          <input
            type="number"
            step="0.01"
            className="input-field"
            value={formData.utility_payment_on_time_rate}
            onChange={(e) =>
              updateField("utility_payment_on_time_rate", Number(e.target.value))
            }
            min={0}
            max={1}
          />
        </div>

        <div>
          <label className="label">
            پرداخت به‌موقع موبایل
            <span className="text-xs text-slate-400 mr-1">(0 تا 1)</span>
          </label>
          <input
            type="number"
            step="0.01"
            className="input-field"
            value={formData.telecom_payment_on_time_rate}
            onChange={(e) =>
              updateField("telecom_payment_on_time_rate", Number(e.target.value))
            }
            min={0}
            max={1}
          />
        </div>

        <div>
          <label className="label">هزینه ماهانه موبایل</label>
          <input
            type="number"
            step="0.1"
            className="input-field"
            value={formData.monthly_avg_telco_charge}
            onChange={(e) =>
              updateField("monthly_avg_telco_charge", Number(e.target.value))
            }
            min={0}
          />
        </div>

        {/* رفتار دیجیتال */}
        <div className="md:col-span-2 lg:col-span-3 mt-4">
          <h3 className="text-sm font-semibold text-slate-600 mb-3 border-b border-slate-200 pb-2">
            رفتار دیجیتال و پس‌انداز
          </h3>
        </div>

        <div>
          <label className="label">
            فعالیت خرید آنلاین
            <span className="text-xs text-slate-400 mr-1">(0 تا 100)</span>
          </label>
          <input
            type="number"
            className="input-field"
            value={formData.ecommerce_activity_score}
            onChange={(e) =>
              updateField("ecommerce_activity_score", Number(e.target.value))
            }
            min={0}
            max={100}
          />
        </div>

        <div>
          <label className="label">
            استفاده از کیف پول دیجیتال
            <span className="text-xs text-slate-400 mr-1">(0 تا 100)</span>
          </label>
          <input
            type="number"
            className="input-field"
            value={formData.digital_wallet_usage_score}
            onChange={(e) =>
              updateField("digital_wallet_usage_score", Number(e.target.value))
            }
            min={0}
            max={100}
          />
        </div>

        <div>
          <label className="label">
            رفتار پس‌انداز
            <span className="text-xs text-slate-400 mr-1">(0 تا 100)</span>
          </label>
          <input
            type="number"
            className="input-field"
            value={formData.savings_behavior_score}
            onChange={(e) =>
              updateField("savings_behavior_score", Number(e.target.value))
            }
            min={0}
            max={100}
          />
        </div>
      </div>

      <div className="mt-8 flex justify-end">
        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              در حال ارزیابی...
            </span>
          ) : (
            "ارزیابی اعتباری و دریافت توضیح"
          )}
        </button>
      </div>
    </form>
  );
}