import { NextRequest, NextResponse } from "next/server";
import { cookieName, cookieOptions, getAuthConfig, readSession, sameOrigin } from "@/lib/auth-server";

/** Strict allowlisted BFF paths. Never a generic attacker-controlled proxy. */
type Context = { params: Promise<{ action?: string[] }> };
const routes: Record<string, readonly string[]> = {
  GET: ["", "analyses", "export"],
  PUT: ["history-consent"],
  DELETE: [""],
};

async function forward(request: NextRequest, context: Context, method: "GET" | "PUT" | "DELETE") {
  let config;
  try { config = getAuthConfig(); } catch {
    return NextResponse.json({ error: "Account service not configured." }, { status: 503 });
  }
  const parts = (await context.params).action || [];
  const action = parts.join("/");
  if (!routes[method].includes(action)) return NextResponse.json({ error: "Not found" }, { status: 404 });
  if (method !== "GET" && !sameOrigin(request, config)) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }
  const session = readSession(request, config);
  if (!session) return NextResponse.json({ error: "Sign-in required." }, { status: 401 });
  let body: string | undefined;
  if (method === "PUT") {
    if (request.headers.get("content-type")?.split(";")[0].trim() !== "application/json") {
      return NextResponse.json({ error: "Expected JSON." }, { status: 415 });
    }
    if (Number(request.headers.get("content-length") || "0") > 1024) {
      return NextResponse.json({ error: "Request too large." }, { status: 413 });
    }
    body = await request.text();
    if (body.length > 1024) return NextResponse.json({ error: "Request too large." }, { status: 413 });
  }
  try {
    const upstream = await fetch(config.apiBase + "/api/v1/account" + (action ? "/" + action : ""), {
      method,
      headers: { Authorization: "Bearer " + session.token, ...(body === undefined ? {} : { "Content-Type": "application/json" }) },
      body,
      cache: "no-store",
      signal: AbortSignal.timeout(8000),
    });
    const response = new NextResponse(upstream.status === 204 ? null : await upstream.text(), {
      status: upstream.status,
      headers: { "Cache-Control": "no-store", ...(upstream.status === 204 ? {} : { "Content-Type": "application/json" }) },
    });
    if (method === "DELETE" && upstream.ok) response.cookies.set(cookieName("session", config), "", cookieOptions(config, 0));
    return response;
  } catch {
    return NextResponse.json({ error: "Account service unavailable." }, { status: 503 });
  }
}

export async function GET(request: NextRequest, context: Context) { return forward(request, context, "GET"); }
export async function PUT(request: NextRequest, context: Context) { return forward(request, context, "PUT"); }
export async function DELETE(request: NextRequest, context: Context) { return forward(request, context, "DELETE"); }
