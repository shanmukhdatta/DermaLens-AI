import { createHash, randomBytes } from "node:crypto";
import type { NextRequest } from "next/server";
import { constantTimeEqual, openCookie, sealCookie } from "./session-crypto";

export type AuthConfig = Readonly<{
  issuer: string;
  clientId: string;
  clientSecret: string;
  appOrigin: string;
  apiBase: string;
  secret: string;
  secure: boolean;
}>;

export function getAuthConfig(): AuthConfig {
  const issuer = process.env.DERMALENS_WEB_OIDC_ISSUER || "";
  const clientId = process.env.DERMALENS_WEB_OIDC_CLIENT_ID || "";
  const clientSecret = process.env.DERMALENS_WEB_OIDC_CLIENT_SECRET || "";
  const appOrigin = process.env.DERMALENS_WEB_APP_ORIGIN || "";
  const apiBase = process.env.DERMALENS_WEB_API_BASE_URL || "";
  const secret = process.env.DERMALENS_WEB_SESSION_KEY || "";
  if (!issuer || !clientId || !clientSecret || !appOrigin || !apiBase || !/^[a-fA-F0-9]{64}$/.test(secret)) {
    throw new Error("OIDC BFF is not configured");
  }
  const i = new URL(issuer);
  const a = new URL(appOrigin);
  const b = new URL(apiBase);
  if (i.protocol !== "https:" || !i.hostname || a.origin !== appOrigin || b.origin !== apiBase) {
    throw new Error("Invalid OIDC BFF URL configuration");
  }
  const local = a.protocol === "http:" && ["localhost", "127.0.0.1"].includes(a.hostname);
  if (!(a.protocol === "https:" || local)) throw new Error("Web app requires HTTPS");
  if (!(b.protocol === "https:" || (local && b.protocol === "http:" && ["localhost", "127.0.0.1"].includes(b.hostname)))) {
    throw new Error("API connection requires HTTPS outside local development");
  }
  return { issuer, clientId, clientSecret, appOrigin, apiBase, secret, secure: a.protocol === "https:" };
}

export function cookieName(kind: "session" | "transaction", config: AuthConfig): string {
  const name = kind === "session" ? "dermalens_session" : "dermalens_oauth";
  return config.secure ? "__Host-" + name : name;
}

export function cookieOptions(config: AuthConfig, maxAge: number, crossSiteCallback = false) {
  return { httpOnly: true, secure: config.secure, sameSite: crossSiteCallback ? ("lax" as const) : ("strict" as const), path: "/", maxAge };
}

export function sameOrigin(request: NextRequest, config: AuthConfig): boolean {
  return request.headers.get("origin") === config.appOrigin;
}

export type Discovery = { issuer: string; authorization_endpoint: string; token_endpoint: string };
export async function discover(config: AuthConfig): Promise<Discovery> {
  const url = config.issuer.replace(/\/$/, "") + "/.well-known/openid-configuration";
  const response = await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(5000) });
  if (!response.ok) throw new Error("Provider discovery failed");
  const body: unknown = await response.json();
  if (typeof body !== "object" || body === null) throw new Error("Invalid OIDC metadata");
  const obj = body as Partial<Discovery>;
  const checkEndpoint = (candidate: unknown): candidate is string => {
    if (typeof candidate !== "string") return false;
    try {
      const u = new URL(candidate);
      return u.protocol === "https:" && u.origin === new URL(config.issuer).origin && !u.username && !u.password && !u.hash;
    } catch { return false; }
  };
  if (obj.issuer !== config.issuer || !checkEndpoint(obj.authorization_endpoint) || !checkEndpoint(obj.token_endpoint)) {
    throw new Error("Provider endpoints do not match configured issuer");
  }
  return obj as Discovery;
}

export function newAuthorization(config: AuthConfig, endpoint: string) {
  const state = randomBytes(32).toString("base64url");
  const verifier = randomBytes(48).toString("base64url");
  const challenge = createHash("sha256").update(verifier).digest("base64url");
  const uri = config.appOrigin + "/api/auth/callback";
  const target = new URL(endpoint);
  target.searchParams.set("client_id", config.clientId);
  target.searchParams.set("redirect_uri", uri);
  target.searchParams.set("response_type", "code");
  target.searchParams.set("scope", "openid");
  target.searchParams.set("state", state);
  target.searchParams.set("code_challenge", challenge);
  target.searchParams.set("code_challenge_method", "S256");
  return { target, state, verifier };
}

export function readTransaction(request: NextRequest, config: AuthConfig, state: string) {
  const value = openCookie(request.cookies.get(cookieName("transaction", config))?.value, "transaction", config.secret);
  if (!value || typeof value !== "object") return null;
  const tx = value as Record<string, unknown>;
  if (typeof tx.state !== "string" || typeof tx.verifier !== "string" || typeof tx.created !== "number") return null;
  if (Date.now() - tx.created > 600_000 || tx.created > Date.now() + 30_000 || !constantTimeEqual(tx.state, state)) return null;
  return tx.verifier;
}

export function transactionCookie(config: AuthConfig, state: string, verifier: string): string {
  return sealCookie({ state, verifier, created: Date.now() }, "transaction", config.secret);
}

export type BrowserSession = { token: string; expires: number };
export function sessionCookie(config: AuthConfig, session: BrowserSession): string {
  return sealCookie(session, "session", config.secret);
}

export function readSession(request: NextRequest, config: AuthConfig): BrowserSession | null {
  const raw = openCookie(request.cookies.get(cookieName("session", config))?.value, "session", config.secret);
  if (!raw || typeof raw !== "object") return null;
  const v = raw as Record<string, unknown>;
  if (typeof v.token !== "string" || v.token.length < 16 || v.token.length > 8192
    || typeof v.expires !== "number" || !Number.isFinite(v.expires)
    || v.expires <= Date.now() / 1000 + 15 || v.expires > Date.now() / 1000 + 3600) return null;
  return { token: v.token, expires: v.expires };
}

export async function verifiedAccount(config: AuthConfig, token: string): Promise<Response> {
  return fetch(config.apiBase + "/api/v1/account", {
    headers: { Authorization: "Bearer " + token },
    cache: "no-store",
    signal: AbortSignal.timeout(5000),
  });
}
