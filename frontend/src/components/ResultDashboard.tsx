import type { CreditExplanationResponse } from "../types/credit";
import { ScoreGauge } from "./ScoreGauge";
import { RiskBadge, DecisionBadge, ProviderBadge } from "./StatusBadges";
import { FactorList } from "./FactorList";
import { RecommendationList } from "./RecommendationList";

interface ResultDashboardProps {
  result: CreditExplanationResponse;
  onReset: () => void;
}

export function ResultDashboard({ result, onReset }: ResultDashboardProps) {
  const defaultProbabilityPercent = (result.default_probability * 100).toFixed(1);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header with actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800">نتیجه ارزیابی اعتباری</h2>
          <p className="text-sm text-slate-500 mt-1">
            شناسه درخواست: <span className="font-mono text-xs" dir="ltr">{result.request_id}</span>
          </p>
        </div>
        <button onClick={onReset} className="btn-secondary">
          درخواست جدید
        </button>
      </div>

      {/* Main Score Card */}
      <div className="card">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Score Gauge */}
          <div className="flex justify-center items-center">
            <ScoreGauge score={result.credit_score} />
          </div>

          {/* Stats */}
          <div className="lg:col-span-2 flex flex-col justify-center">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Decision */}
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-xs text-slate-500 mb-2">تصمیم سیستم</p>
                <DecisionBadge decision={result.decision} />
              </div>

              {/* Risk Level */}
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-xs text-slate-500 mb-2">سطح ریسک</p>
                <RiskBadge riskLevel={result.risk_level} />
              </div>

              {/* Default Probability */}
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-xs text-slate-500 mb-1">احتمال نکول</p>
                <p className="text-2xl font-bold text-slate-800">
                  {defaultProbabilityPercent}٪
                </p>
                <div className="mt-2 w-full bg-slate-200 rounded-full h-2">
                  <div
                    className="bg-bank-danger h-2 rounded-full transition-all duration-500"
                    style={{ width: `${defaultProbabilityPercent}%` }}
                  />
                </div>
              </div>

              {/* Provider */}
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-xs text-slate-500 mb-2">منبع توضیح</p>
                <ProviderBadge provider={result.generated_by} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="card border-r-4 border-r-bank-primary">
        <h3 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
          <svg className="w-5 h-5 text-bank-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          خلاصه ارزیابی
        </h3>
        <p className="text-slate-700 leading-relaxed">{result.summary}</p>
      </div>

      {/* Messages Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Customer Message */}
        <div className="card border-r-4 border-r-green-500">
          <h3 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            پیام برای مشتری
          </h3>
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-green-900 leading-relaxed text-sm">
              {result.customer_message}
            </p>
          </div>
        </div>

        {/* Employee Note */}
        <div className="card border-r-4 border-r-blue-500">
          <h3 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            یادداشت کارمند بانک
          </h3>
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-blue-900 leading-relaxed text-sm">
              {result.employee_note}
            </p>
          </div>
        </div>
      </div>

      {/* Factors */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-bank-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          عوامل مؤثر بر تصمیم ({result.factors.length} عامل)
        </h3>
        <FactorList factors={result.factors} />
      </div>

      {/* Recommendations */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-bank-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          توصیه‌های بهبود ({result.recommendations.length} توصیه)
        </h3>
        <RecommendationList recommendations={result.recommendations} />
      </div>

      {/* Timestamp */}
      <div className="text-center text-xs text-slate-400">
        زمان ارزیابی: {new Date(result.timestamp).toLocaleString("fa-IR")}
      </div>
    </div>
  );
}