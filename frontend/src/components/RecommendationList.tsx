interface RecommendationListProps {
  recommendations: string[];
}

export function RecommendationList({ recommendations }: RecommendationListProps) {
  if (recommendations.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      {recommendations.map((recommendation, index) => (
        <div
          key={index}
          className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg border border-blue-100"
        >
          <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
            {index + 1}
          </span>
          <p className="text-sm text-blue-900 leading-relaxed">
            {recommendation}
          </p>
        </div>
      ))}
    </div>
  );
}