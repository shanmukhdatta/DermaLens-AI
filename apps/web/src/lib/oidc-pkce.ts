/** Browser OAuth2/OIDC public-client PKCE. Tokens stay in React memory, never storage. */
export type OidcPublicConfig = {
  authorizationEndpoint: string;
  tokenEndpoint: string;
  clientId: string;
  audience?: string;
};

const PKCE_STORAGE_KEY = "dermalens-oidc-pkce";
const MAX_CALLBACK_AGE_MS = 10 * 60 * 1000;

function secureEndpoint(input: string): string {
  const url = new URL(input);
  const loopback = url.hostname === "localhost" || url.hostname === "127.0.0.1";
  if ((url.protocol !== "https:" && !(loopback && url.protocol === "http:"))
    || !url.hostname || url.username || url.password || url.hash) {
    throw new Error("OIDC endpoints must use HTTPS (except local development).");
  }
  return url.toString();
}

export function validateOidcConfig(config: OidcPublicConfig): OidcPublicConfig {
  if (!config.clientId || config.clientId.length > 250) {
    throw new Error("OIDC public client ID is missing.");
  }
  return {
    ...config,
    authorizationEndpoint: secureEndpoint(config.authorizationEndpoint),
    tokenEndpoint: secureEndpoint(config.tokenEndpoint),
  };
}

export function configuredOidc(): OidcPublicConfig | null {
  const authorizationEndpoint = process.env.NEXT_PUBLIC_OIDC_AUTHORIZATION_URL;
  const tokenEndpoint = process.env.NEXT_PUBLIC_OIDC_TOKEN_URL;
  const clientId = process.env.NEXT_PUBLIC_OIDC_CLIENT_ID;
  if (!authorizationEndpoint || !tokenEndpoint || !clientId) return null;
  return validateOidcConfig({
    authorizationEndpoint,
    tokenEndpoint,
    clientId,
    audience: process.env.NEXT_PUBLIC_OIDC_AUDIENCE || undefined,
  });
}

function encodeUrlSafe(bytes: Uint8Array): string {
  return btoa(Array.from(bytes, byte => String.fromCharCode(byte)).join(""))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function randomString(): string {
  const data = new Uint8Array(48);
  crypto.getRandomValues(data);
  return encodeUrlSafe(data);
}

function callbackUrl(): string {
  return new URL("/auth/callback", window.location.origin).toString();
}

export async function startOidcLogin(config: OidcPublicConfig): Promise<void> {
  const safe = validateOidcConfig(config);
  const state = randomString();
  const nonce = randomString();
  const verifier = randomString();
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier));
  const challenge = encodeUrlSafe(new Uint8Array(digest));
  window.sessionStorage.setItem(PKCE_STORAGE_KEY, JSON.stringify({
    state, verifier, issuedAt: Date.now(),
  }));
  const url = new URL(safe.authorizationEndpoint);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("client_id", safe.clientId);
  url.searchParams.set("redirect_uri", callbackUrl());
  url.searchParams.set("scope", "openid profile");
  url.searchParams.set("code_challenge_method", "S256");
  url.searchParams.set("code_challenge", challenge);
  url.searchParams.set("state", state);
  url.searchParams.set("nonce", nonce);
  if (safe.audience) url.searchParams.set("audience", safe.audience);
  window.location.assign(url.toString());
}

export type OidcAccessToken = { accessToken: string; expiresAt: number };

export async function completeOidcLogin(
  config: OidcPublicConfig, apiBase: string
): Promise<OidcAccessToken> {
  const safe = validateOidcConfig(config);
  const params = new URLSearchParams(window.location.search);
  const saved = window.sessionStorage.getItem(PKCE_STORAGE_KEY);
  window.sessionStorage.removeItem(PKCE_STORAGE_KEY);
  window.history.replaceState({}, "", "/auth/callback");
  if (params.get("error") || !saved) throw new Error("Sign-in was cancelled or expired.");
  let state: { state: string; verifier: string; issuedAt: number };
  try { state = JSON.parse(saved) as typeof state; }
  catch { throw new Error("Invalid sign-in state."); }
  if (!state || typeof state.state !== "string" || typeof state.verifier !== "string"
    || !Number.isFinite(state.issuedAt) || Date.now() - state.issuedAt > MAX_CALLBACK_AGE_MS
    || Date.now() < state.issuedAt || params.get("state") !== state.state
    || !params.get("code")) {
    throw new Error("The identity-provider response failed validation.");
  }
  const body = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: safe.clientId,
    redirect_uri: callbackUrl(),
    code: params.get("code") || "",
    code_verifier: state.verifier,
  });
  const response = await fetch(safe.tokenEndpoint, {
    method: "POST",
    body, headers: { "Content-Type": "application/x-www-form-urlencoded" },
    cache: "no-store",
  });
  if (!response.ok) throw new Error("The identity provider could not complete sign-in.");
  const raw: unknown = await response.json();
  if (!raw || typeof raw !== "object") throw new Error("Invalid identity-provider response.");
  const token = raw as Record<string, unknown>;
  if (typeof token.access_token !== "string" || token.access_token.length < 16
    || token.token_type !== "Bearer" || typeof token.expires_in !== "number"
    || !Number.isFinite(token.expires_in) || token.expires_in < 30
    || token.expires_in > 86_400) {
    throw new Error("Unsupported identity-provider token response.");
  }
  // The backend is the authority for issuer, signature and audience, not this browser.
  const verify = await fetch(apiBase.replace(/\/$/, "") + "/api/v1/account", {
    headers: { Authorization: "Bearer " + token.access_token },
    cache: "no-store",
  });
  if (!verify.ok) throw new Error("Sign-in token was not accepted by DermaLens.");
  return {
    accessToken: token.access_token,
    expiresAt: Date.now() + Math.max(0, token.expires_in - 30) * 1000,
  };
}
