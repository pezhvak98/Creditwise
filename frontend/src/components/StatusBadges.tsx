import type { RiskLevel, Decision, ExplanationProvider } from "../types/credit";

interface RiskBadgeProps {
  riskLevel: RiskLevel;
}

export function RiskBadge({ riskLevel }: RiskBadgeProps) {
  const config = {
    low: { label: "ریسک کم", className: "bg-green-100 text-green-800 border-green-200" },
    medium: { label: "ریسک متوسط", className: "bg-amber-100 text-amber-800 border-amber-200" },
    high: { label: "ریسک زیاد", className: "bg-red-100 text-red-800 border-red-200" },
  };

  const { label, className } = config[riskLevel];

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${className}`}>
      <span className="w-2 h-2 rounded-full mr-2 bg-current" />
      {label}
    </span>
  );
}

interface DecisionBadgeProps {
  decision: Decision;
}

export function DecisionBadge({ decision }: DecisionBadgeProps) {
  const config = {
    approve: {
      label: "تأیید اولیه",
      className: "bg-green-100 text-green-800",
      icon: "✓",
    },
    review: {
      label: "بررسی تکمیلی",
      className: "bg-amber-100 text-amber-800",
      icon: "!",
    },
    decline: {
      label: "عدم تأیید اولیه",
      className: "bg-red-100 text-red-800",
      icon: "✕",
    },
  };

  const { label, className, icon } = config[decision];

  return (
    <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold ${className}`}>
      <span className="text-lg">{icon}</span>
      {label}
    </span>
  );
}

interface ProviderBadgeProps {
  provider: ExplanationProvider;
}

export function ProviderBadge({ provider }: ProviderBadgeProps) {
  if (provider === "openai") {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
        <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse" />
        توضیح توسط LLM
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
      <span className="w-1.5 h-1.5 rounded-full bg-slate-500" />
      توضیح قانون‌محور
    </span>
  );
}