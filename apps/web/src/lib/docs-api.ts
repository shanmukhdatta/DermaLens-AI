export type DocumentMatch = Readonly<{ path: string; section: string; excerpt: string }>;

export type DocumentationSearch = Readonly<{
  status: "matches" | "no_match";
  matches: DocumentMatch[];
  notice: string;
}>;

export function validateDocsQuestion(question: string): string | null {
  const value = question.trim();
  if (value.length < 4) return "Enter at least four characters.";
  if (value.length > 180) return "Keep your question below 181 characters.";
  return null;
}

export async function searchProjectDocs(question: string, signal?: AbortSignal): Promise<DocumentationSearch> {
  const error = validateDocsQuestion(question);
  if (error) throw new Error(error);
  const base = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  let response: Response;
  try {
    response = await fetch(base + "/api/v1/docs/search?q=" + encodeURIComponent(question.trim()), {
      method: "GET", cache: "no-store", signal,
    });
  } catch {
    throw new Error("The documentation service is currently unreachable.");
  }
  if (!response.ok) throw new Error("The documentation service is unavailable.");
  const payload: unknown = await response.json().catch(() => null);
  if (!payload || typeof payload !== "object" || !("matches" in payload)
    || !Array.isArray(payload.matches) || !("status" in payload)) {
    throw new Error("Unexpected documentation response.");
  }
  if (payload.status !== "matches" && payload.status !== "no_match") {
    throw new Error("Unexpected documentation response.");
  }
  const sourcePaths = new Set([
    "README.md", "docs/01_SYSTEM_ARCHITECTURE.md", "docs/02_COMPUTER_VISION_PIPELINE.md",
    "docs/03_MODEL_AND_RESEARCH.md", "docs/04_BACKEND_ARCHITECTURE.md",
    "docs/05_RAG_ASSISTANT.md", "docs/06_FEEDBACK_AND_CONTINUAL_LEARNING.md",
    "docs/07_MLOPS_AND_DEPLOYMENT.md", "docs/08_API_AND_DATA_FLOW.md",
    "docs/09_PRIVACY_AND_SAFETY.md",
  ]);
  if (payload.matches.length > 3 || payload.matches.some((item: unknown) => {
    if (!item || typeof item !== "object") return true;
    const value = item as Record<string, unknown>;
    return typeof value.path !== "string" || !sourcePaths.has(value.path)
      || typeof value.section !== "string" || typeof value.excerpt !== "string"
      || value.excerpt.length > 650;
  })) throw new Error("Unexpected documentation response.");
  return {
    status: payload.status,
    matches: payload.matches as DocumentMatch[],
    notice: "Public project documentation only. No medical advice or image assessment.",
  };
}
