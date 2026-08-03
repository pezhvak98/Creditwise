interface ScoreGaugeProps {
  score: number;
  maxScore?: number;
  minScore?: number;
}

export function ScoreGauge({
  score,
  maxScore = 850,
  minScore = 300,
}: ScoreGaugeProps) {
  const percentage = ((score - minScore) / (maxScore - minScore)) * 100;
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const getColor = () => {
    if (percentage >= 70) return "#10b981"; // green
    if (percentage >= 40) return "#f59e0b"; // amber
    return "#ef4444"; // red
  };

  const color = getColor();

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-44 h-44">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 160 160">
          {/* Background circle */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke="#e2e8f0"
            strokeWidth="12"
            fill="none"
          />
          {/* Progress circle */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke={color}
            strokeWidth="12"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold" style={{ color }}>
            {score}
          </span>
          <span className="text-xs text-slate-500 mt-1">از {maxScore}</span>
        </div>
      </div>
      <p className="mt-3 text-sm text-slate-600">امتیاز اعتباری</p>
    </div>
  );
}