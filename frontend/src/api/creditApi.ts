import type { CreditApplicationRequest, CreditExplanationResponse } from "../types/credit";

const API_BASE_URL = "http://localhost:8000/api/v1";

class CreditApi {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async explainCredit(
    application: CreditApplicationRequest
  ): Promise<CreditExplanationResponse> {
    const response = await fetch(`${this.baseUrl}/credit/explain`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ application }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `API request failed (${response.status}): ${errorText}`
      );
    }

    return response.json();
  }

  async health(): Promise<{ status: string; model_ready: boolean }> {
    const response = await fetch("http://localhost:8000/health");

    if (!response.ok) {
      throw new Error("Backend health check failed");
    }

    return response.json();
  }
}

export const creditApi = new CreditApi();