import { useState } from "react";
import { ApplicationForm } from "./components/ApplicationForm";
import { ResultDashboard } from "./components/ResultDashboard";
import { creditApi } from "./api/creditApi";
import type {
  CreditApplicationRequest,
  CreditExplanationResponse,
} from "./types/credit";

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CreditExplanationResponse | null>(null);
  const [showForm, setShowForm] = useState(true);

  const handleSubmit = async (application: CreditApplicationRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await creditApi.explainCredit(application);
      setResult(response);
      setShowForm(false);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "خطای ناشناخته در ارتباط با سرور"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setShowForm(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 py-5">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-bank-primary to-bank-secondary rounded-xl flex items-center justify-center">
              <svg
                className="w-7 h-7 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-bank-primary">
                CreditWise
              </h1>
              <p className="text-sm text-slate-500">
                سامانه هوشمند امتیازدهی اعتباری جایگزین با توضیح‌پذیری
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {showForm ? (
          <>
            <ApplicationForm onSubmit={handleSubmit} isLoading={isLoading} />

            {error && (
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
                <p className="font-medium">خطا در پردازش درخواست</p>
                <p className="text-sm mt-1">{error}</p>
              </div>
            )}
          </>
        ) : (
          result && <ResultDashboard result={result} onReset={handleReset} />
        )}
      </main>

      {/* Footer */}
      <footer className="max-w-6xl mx-auto px-4 py-6 text-center text-sm text-slate-500">
        <p>
          Pezhvak • Powered by FastAPI + React + Local LLM
        </p>
      </footer>
    </div>
  );
}

export default App;