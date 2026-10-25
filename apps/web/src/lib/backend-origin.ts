/** Server-only API origin. Never accept a backend host from a browser parameter. */
export function getBackendOrigin(
  configured = process.env.DERMALENS_WEB_API_BASE_URL,
  environment = process.env.NODE_ENV
): string | null {
  const input = configured || (environment === "production" ? null : "http://127.0.0.1:8000");
  if (!input) return null;
  try {
    const url = new URL(input);
    if (!["http:", "https:"].includes(url.protocol) || url.username || url.password ||
        url.pathname !== "/" || url.search || url.hash) return null;
    if (environment === "production" && url.protocol !== "https:") return null;
    return url.origin;
  } catch {
    return null;
  }
}
