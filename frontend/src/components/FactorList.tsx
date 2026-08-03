import type { FeatureFactor } from "../types/credit";

interface FactorListProps {
  factors: FeatureFactor[];
}

export function FactorList({ factors }: FactorListProps) {
  const getDirectionStyles = (direction: FeatureFactor["direction"]) => {
    switch (direction) {
      case "positive":
        return {
          icon: "↑",
          iconColor: "text-green-600",
          badgeColor: "bg-green-50 text-green-700 border-green-200",
          label: "مثبت",
        };
      case "negative":
        return {
          icon: "↓",
          iconColor: "text-red-600",
          badgeColor: "bg-red-50 text-red-700 border-red-200",
          label: "نیازمند توجه",
        };
      default:
        return {
          icon: "→",
          iconColor: "text-slate-500",
          badgeColor: "bg-slate-50 text-slate-600 border-slate-200",
          label: "خنثی",
        };
    }
  };

  return (
    <div className="space-y-3">
      {factors.map((factor, index) => {
        const styles = getDirectionStyles(factor.direction);

        return (
          <div
            key={`${factor.feature}-${index}`}
            className="flex items-start gap-3 p-4 bg-white rounded-lg border border-slate-200 hover:border-slate-300 transition-colors"
          >
            <span className={`text-xl font-bold ${styles.iconColor}`}>
              {styles.icon}
            </span>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-slate-800">{factor.title}</h4>
                <span className={`text-xs px-2 py-0.5 rounded-full border ${styles.badgeColor}`}>
                  {styles.label}
                </span>
              </div>
              <p className="text-sm text-slate-600 mt-1 leading-relaxed">
                {factor.description}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}