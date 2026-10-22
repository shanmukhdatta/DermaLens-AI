/** Typed authenticated API client. No token persistence, URL parameters or logging. */
const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000")
  .replace(/\/$/, "");

export type HistoryItem = {
  id: string;
  status: string;
  model_version: string | null;
  pipeline_version: string | null;
  created_at: string;
};

export type ExperimentalResult = {
  analysis_id: string;
  status: string;
  decision: "RESEARCH_ONLY_UNCALIBRATED";
  research_category: string;
  raw_model_score: number;
  notice: string;
  medical_diagnosis: false;
  created_at: string;
  model: { id: string; version: string };
};

export class ResearchApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = "ResearchApiError";
  }
}

async function request(token: string, path: string, init?: RequestInit): Promise<unknown> {
  if (!token || !path.startsWith("/api/v1/")) {
    throw new ResearchApiError("Invalid authenticated request.", 400);
  }
  let response: Response;
  try {
    response = await fetch(API_BASE + path, {
      ...init,
      cache: "no-store",
      headers: { ...(init?.headers || {}), Authorization: "Bearer " + token },
    });
  } catch {
    throw new ResearchApiError("The research API is unavailable.", 503);
  }
  if (!response.ok) {
    const message = response.status === 401 ? "Your session has expired or was rejected."
      : response.status === 403 ? "Enable history consent to store research results."
      : response.status === 404 ? "This record is not available to your account."
      : response.status === 413 ? "The photo exceeds the size limit."
      : response.status === 422 ? "The submitted image did not pass quality validation."
      : response.status === 429 ? "Please reduce request frequency."
      : response.status === 503 ? "Experimental analysis is not enabled in this deployment."
      : "The operation could not be completed.";
    throw new ResearchApiError(message, response.status);
  }
  if (response.status === 204) return null;
  return response.json();
}

export async function getAccount(token: string): Promise<{ history_enabled: boolean }> {
  const data = await request(token, "/api/v1/account");
  if (!data || typeof data !== "object" || !("history_enabled" in data)
    || typeof data.history_enabled !== "boolean") {
    throw new ResearchApiError("Unexpected account response.", 502);
  }
  return { history_enabled: data.history_enabled };
}

export async function setHistoryConsent(token: string, enabled: boolean): Promise<boolean> {
  const data = await request(token, "/api/v1/account/history-consent", {
    method: "PUT", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ enabled }),
  });
  return Boolean(data && typeof data === "object"
    && "history_enabled" in data && data.history_enabled === enabled);
}

export async function listHistory(token: string): Promise<HistoryItem[]> {
  const data = await request(token, "/api/v1/account/analyses");
  if (!data || typeof data !== "object" || !("items" in data) || !Array.isArray(data.items)) {
    throw new ResearchApiError("Unexpected history response.", 502);
  }
  return data.items as HistoryItem[];
}

export async function submitResearchImage(token: string, file: File): Promise<ExperimentalResult> {
  const raw = await request(token, "/api/v1/analyses", {
    method: "POST", body: file, headers: { "Content-Type": file.type },
  });
  if (!raw || typeof raw !== "object" || !("medical_diagnosis" in raw)
    || raw.medical_diagnosis !== false || !("decision" in raw)
    || raw.decision !== "RESEARCH_ONLY_UNCALIBRATED") {
    throw new ResearchApiError("Unexpected nonclinical research result.", 502);
  }
  return raw as ExperimentalResult;
}

export async function getResearchResult(token: string, id: string): Promise<ExperimentalResult> {
  const raw = await request(token, "/api/v1/analyses/" + encodeURIComponent(id));
  if (!raw || typeof raw !== "object" || !("medical_diagnosis" in raw)
    || raw.medical_diagnosis !== false || !("analysis_id" in raw)
    || raw.analysis_id !== id) {
    throw new ResearchApiError("Unexpected private result response.", 502);
  }
  return raw as ExperimentalResult;
}

export async function deleteResearchResult(token: string, id: string): Promise<void> {
  await request(token, "/api/v1/analyses/" + encodeURIComponent(id), { method: "DELETE" });
}

export async function eraseAccount(token: string): Promise<void> {
  await request(token, "/api/v1/account", { method: "DELETE" });
}

export async function exportPrivateHistory(token: string): Promise<unknown> {
  return request(token, "/api/v1/account/export");
}
