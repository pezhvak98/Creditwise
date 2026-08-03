import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { CreditApplicationRequest } from "../../types/credit";

interface CreditRadarChartProps {
  application: CreditApplicationRequest;
  creditScore: number;
}

export function CreditRadarChart({ application, creditScore }: CreditRadarChartProps) {
  const data = [
    {
      subject: "پرداخت قبوض",
      value: application.utility_payment_on_time_rate * 100,
      fullMark: 100,
    },
    {
      subject: "پرداخت موبایل",
      value: application.telecom_payment_on_time_rate * 100,
      fullMark: 100,
    },
    {
      subject: "پرداخت اجاره",
      value: application.has_rent_history
        ? (application.rent_payment_on_time_rate ?? 0) * 100
        : 0,
      fullMark: 100,
    },
    {
      subject: "پس‌انداز",
      value: application.savings_behavior_score,
      fullMark: 100,
    },
    {
      subject: "رفتار دیجیتال",
      value: application.digital_wallet_usage_score,
      fullMark: 100,
    },
    {
      subject: "امتیاز اعتباری",
      value: ((creditScore - 300) / (850 - 300)) * 100,
      fullMark: 100,
    },
  ];

  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: "#64748b", fontSize: 12, fontFamily: "Vazirmatn" }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: "#94a3b8", fontSize: 10 }}
            tickCount={5}
          />
          <Radar
            name="پروفایل اعتباری"
            dataKey="value"
            stroke="#1e40af"
            fill="#3b82f6"
            fillOpacity={0.4}
            strokeWidth={2}
          />
          <Tooltip
            formatter={(value) => {
              const numValue = typeof value === "number" ? value : Number(value) || 0;
              return [`${numValue.toFixed(0)}٪`, "مقدار"];
            }}
            contentStyle={{
              fontFamily: "Vazirmatn",
              direction: "rtl",
              borderRadius: "8px",
              border: "1px solid #e2e8f0",
            }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}