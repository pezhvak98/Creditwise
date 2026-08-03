import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import type { FeatureFactor } from "../../types/credit";

interface FactorDistributionChartProps {
  factors: FeatureFactor[];
}

const COLORS = {
  positive: "#10b981",
  negative: "#ef4444",
  neutral: "#94a3b8",
};

export function FactorDistributionChart({ factors }: FactorDistributionChartProps) {
  const counts = factors.reduce(
    (acc, factor) => {
      acc[factor.direction] = (acc[factor.direction] || 0) + 1;
      return acc;
    },
    { positive: 0, negative: 0, neutral: 0 } as Record<string, number>
  );

  const data = [
    { name: "مثبت", value: counts.positive, color: COLORS.positive },
    { name: "نیازمند توجه", value: counts.negative, color: COLORS.negative },
    { name: "خنثی", value: counts.neutral, color: COLORS.neutral },
  ].filter((item) => item.value > 0);

  if (data.length === 0) return null;

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => {
              const numValue = typeof value === "number" ? value : Number(value) || 0;
              return [`${numValue} عامل`, "تعداد"];
            }}
            contentStyle={{
              fontFamily: "Vazirmatn",
              direction: "rtl",
              borderRadius: "8px",
              border: "1px solid #e2e8f0",
            }}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value) => (
              <span style={{ fontFamily: "Vazirmatn", fontSize: "12px" }}>
                {value}
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}