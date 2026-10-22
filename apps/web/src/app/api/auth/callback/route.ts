import { NextRequest, NextResponse } from "next/server";
import { cookieName, cookieOptions, discover, getAuthConfig, readTransaction, sessionCookie, verifiedAccount } from "@/lib/auth-server";

export async function GET(request: NextRequest) {
  let config;
  try { config = getAuthConfig(); } catch {
    return NextResponse.json({ error: "Sign-in is not configured." }, { status: 503 });
  }
  const state = request.nextUrl.searchParams.get("state") || "";
  const code = request.nextUrl.searchParams.get("code") || "";
  const verifier = readTransaction(request, config, state);
  const failure = (status: number) => {
    const response = NextResponse.json({ error: "Could not complete verified sign-in." }, { status });
    response.cookies.set(cookieName("transaction", config), "", cookieOptions(config, 0, true));
    response.headers.set("Cache-Control", "no-store");
    return response;
  };
  if (!verifier || !code || code.length > 4096 || request.nextUrl.searchParams.has("error")) return failure(400);
  try {
    const metadata = await discover(config);
    const body = new URLSearchParams({
      grant_type: "authorization_code",
      code,
      redirect_uri: config.appOrigin + "/api/auth/callback",
      client_id: config.clientId,
      code_verifier: verifier,
    });
    const basic = Buffer.from(config.clientId + ":" + config.clientSecret).toString("base64");
    const exchange = await fetch(metadata.token_endpoint, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded", Authorization: "Basic " + basic },
      body,
      cache: "no-store",
      signal: AbortSignal.timeout(8000),
    });
    if (!exchange.ok) return failure(401);
    const payload: unknown = await exchange.json();
    if (!payload || typeof payload !== "object") return failure(401);
    const token = payload as Record<string, unknown>;
    if (token.token_type !== "Bearer" || typeof token.access_token !== "string"
      || token.access_token.length < 16 || token.access_token.length > 8192
      || typeof token.expires_in !== "number" || !Number.isInteger(token.expires_in)
      || token.expires_in < 60 || token.expires_in > 3600) return failure(401);
    // FastAPI independently verifies RS256 issuer, audience and subject and rejects opaque/untrusted tokens.
    const account = await verifiedAccount(config, token.access_token);
    if (!account.ok) return failure(account.status === 401 ? 401 : 503);
    const response = NextResponse.redirect(config.appOrigin + "/history");
    response.cookies.set(cookieName("transaction", config), "", cookieOptions(config, 0, true));
    const ttl = Math.min(token.expires_in - 30, 3570);
    response.cookies.set(cookieName("session", config),
      sessionCookie(config, { token: token.access_token, expires: Date.now() / 1000 + ttl }), cookieOptions(config, ttl));
    response.headers.set("Cache-Control", "no-store");
    return response;
  } catch {
    return failure(503);
  }
}
