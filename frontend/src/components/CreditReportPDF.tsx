import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
  Font,
} from "@react-pdf/renderer";
import type { CreditExplanationResponse, CreditApplicationRequest } from "../types/credit";

// Register Vazirmatn font for Persian text
Font.register({
  family: "Vazirmatn",
  fonts: [
    {
      src: "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/ttf/Vazirmatn-Regular.ttf",
      fontWeight: "normal",
    },
    {
      src: "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/ttf/Vazirmatn-Bold.ttf",
      fontWeight: "bold",
    },
  ],
});

const styles = StyleSheet.create({
  page: {
    flexDirection: "column",
    backgroundColor: "#ffffff",
    padding: 40,
    fontFamily: "Vazirmatn",
    textAlign: "right",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 20,
    borderBottom: "2px solid #1e40af",
    paddingBottom: 15,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#1e40af",
    textAlign: "right",
  },
  headerSubtitle: {
    fontSize: 10,
    color: "#64748b",
    marginTop: 4,
    textAlign: "right",
  },
  logoBox: {
    width: 40,
    height: 40,
    backgroundColor: "#1e40af",
    borderRadius: 8,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  logoText: {
    color: "#ffffff",
    fontSize: 18,
    fontWeight: "bold",
  },
  section: {
    marginBottom: 16,
    textAlign: "right",
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: "bold",
    color: "#1e40af",
    marginBottom: 8,
    borderBottom: "1px solid #e2e8f0",
    paddingBottom: 4,
    textAlign: "right",
  },
  scoreContainer: {
    flexDirection: "row",
    justifyContent: "space-around",
    backgroundColor: "#f8fafc",
    borderRadius: 8,
    padding: 15,
    marginBottom: 16,
  },
  scoreItem: {
    alignItems: "center",
    textAlign: "center",
  },
  scoreLabel: {
    fontSize: 9,
    color: "#64748b",
    marginBottom: 4,
    textAlign: "center",
  },
  scoreValue: {
    fontSize: 20,
    fontWeight: "bold",
    textAlign: "center",
  },
  textBlock: {
    fontSize: 10,
    lineHeight: 1.6,
    color: "#334155",
    textAlign: "right",
  },
  cardBox: {
    backgroundColor: "#f8fafc",
    borderRadius: 6,
    padding: 12,
    marginBottom: 8,
    textAlign: "right",
  },
  factorRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: 6,
    fontSize: 10,
    textAlign: "right",
  },
  factorIcon: {
    width: 16,
    marginLeft: 6,
    fontSize: 12,
    textAlign: "right",
  },
  factorTitle: {
    fontWeight: "bold",
    marginLeft: 4,
    textAlign: "right",
  },
  footer: {
    position: "absolute",
    bottom: 20,
    left: 40,
    right: 40,
    textAlign: "center",
    fontSize: 8,
    color: "#94a3b8",
    borderTop: "1px solid #e2e8f0",
    paddingTop: 8,
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
    fontSize: 9,
    fontWeight: "bold",
    textAlign: "center",
  },
  badgeGreen: {
    backgroundColor: "#d1fae5",
    color: "#065f46",
  },
  badgeAmber: {
    backgroundColor: "#fef3c7",
    color: "#92400e",
  },
  badgeRed: {
    backgroundColor: "#fee2e2",
    color: "#991b1b",
  },
});

interface CreditReportPDFProps {
  result: CreditExplanationResponse;
  application: CreditApplicationRequest;
}

export function CreditReportPDF({ result, application }: CreditReportPDFProps) {
  const riskLabel = {
    low: "کم",
    medium: "متوسط",
    high: "زیاد",
  }[result.risk_level];

  const decisionLabel = {
    approve: "تأیید اولیه",
    review: "بررسی تکمیلی",
    decline: "عدم تأیید اولیه",
  }[result.decision];

    const getDecisionBadgeStyle = () => {
    switch (result.decision) {
      case "approve":
        return styles.badgeGreen;
      case "review":
        return styles.badgeAmber;
      default:
        return styles.badgeRed;
    }
  };

  const getFactorIcon = (direction: string) => {
    switch (direction) {
      case "positive":
        return { symbol: "▲", color: "#10b981" };
      case "negative":
        return { symbol: "▼", color: "#ef4444" };
      default:
        return { symbol: "►", color: "#94a3b8" };
    }
  };

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.headerTitle}>CreditWise</Text>
            <Text style={styles.headerSubtitle}>
              گزارش ارزیابی اعتباری با هوش مصنوعی توضیح‌پذیر
            </Text>
          </View>
          <View style={styles.logoBox}>
            <Text style={styles.logoText}>CW</Text>
          </View>
        </View>

        {/* Meta Info */}
        <View style={styles.section}>
          <Text style={[styles.textBlock, { fontSize: 9, color: "#64748b" }]}>
            شناسه درخواست: {result.request_id} | زمان ارزیابی:{" "}
            {new Date(result.timestamp).toLocaleString("fa-IR")}
          </Text>
        </View>

        {/* Score Summary */}
        <View style={styles.scoreContainer}>
          <View style={styles.scoreItem}>
            <Text style={styles.scoreLabel}>امتیاز اعتباری</Text>
            <Text style={[styles.scoreValue, { color: "#1e40af" }]}>
              {result.credit_score}
            </Text>
          </View>
          <View style={styles.scoreItem}>
            <Text style={styles.scoreLabel}>احتمال نکول</Text>
            <Text style={[styles.scoreValue, { color: "#ef4444" }]}>
              {(result.default_probability * 100).toFixed(1)}٪
            </Text>
          </View>
          <View style={styles.scoreItem}>
            <Text style={styles.scoreLabel}>سطح ریسک</Text>
            <Text style={[styles.scoreValue, { color: "#f59e0b" }]}>
              {riskLabel}
            </Text>
          </View>
          <View style={styles.scoreItem}>
            <Text style={styles.scoreLabel}>تصمیم سیستم</Text>
           <Text style={[styles.badge, getDecisionBadgeStyle()]}>
              {decisionLabel}
            </Text>
          </View>
        </View>

        {/* Summary */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>خلاصه ارزیابی</Text>
          <Text style={styles.textBlock}>{result.summary}</Text>
        </View>

        {/* Customer Message */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>پیام برای مشتری</Text>
          <View style={styles.cardBox}>
            <Text style={styles.textBlock}>{result.customer_message}</Text>
          </View>
        </View>

        {/* Employee Note */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>یادداشت کارمند بانک</Text>
          <View style={styles.cardBox}>
            <Text style={styles.textBlock}>{result.employee_note}</Text>
          </View>
        </View>

        {/* Factors */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            عوامل مؤثر بر تصمیم ({result.factors.length} عامل)
          </Text>
          {result.factors.map((factor, index) => {
            const icon = getFactorIcon(factor.direction);
            return (
              <View key={index} style={styles.factorRow}>
                <Text style={[styles.factorIcon, { color: icon.color }]}>
                  {icon.symbol}
                </Text>
                <View style={{ flex: 1, textAlign: "right" }}>
                  <Text style={[styles.textBlock]}>
                    <Text style={styles.factorTitle}>{factor.title}: </Text>
                    {factor.description}
                  </Text>
                </View>
              </View>
            );
          })}
        </View>

        {/* Recommendations */}
        {result.recommendations.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>
              توصیه‌های بهبود ({result.recommendations.length} توصیه)
            </Text>
            {result.recommendations.map((rec, index) => (
              <Text
                key={index}
                style={[styles.textBlock, { marginBottom: 4, textAlign: "right" }]}
              >
                {index + 1}. {rec}
              </Text>
            ))}
          </View>
        )}

        {/* Footer */}
        <Text style={styles.footer}>
          این گزارش توسط سامانه CreditWise و با استفاده از هوش مصنوعی تولید شده است.
          تصمیم نهایی با بانک است. | نسخه 0.1.0
        </Text>
      </Page>
    </Document>
  );
}