import { getToken } from "next-auth/jwt";
import type { NextRequest } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const MAX_IMAGE_BYTES = 8 * 1024 * 1024;
const UUID_PATTERN = /^[0-9a-fA-F-]{36}$/;

type Endpoint = { path: string; permitted: boolean };

function allowed(method: string, parts: string[]): Endpoint {
  const path = parts.join("/");
  if (method === "GET" && [
    "account", "account/analyses", "account/export",
  ].includes(path)) return { path, permitted: true };
  if (method === "PUT" && path === "account/history-consent") {
    return { path, permitted: true };
  }
  if (method === "POST" && path === "analyses") return { path, permitted: true };
  if (method === "DELETE" && path === "account") return { path, permitted: true };
  if (parts.length === 2 && parts[0] === "analyses" &&
      UUID_PATTERN.test(parts[1]) && ["GET", "DELETE"].includes(method)) {
    return { path, permitted: true };
  }
  return { path: "", permitted: false };
}

async function forward(req: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path: parts } = await context.params;
  const endpoint = allowed(req.method, parts);
  if (!endpoint.permitted) return Response.json({ error: "NOT_FOUND" }, { status: 404 });
  const secret = process.env.AUTH_SECRET;
  const backend = process.env.DERMALENS_INTERNAL_API_URL;
  if (!secret || !backend || !/^https?:\/\/[^/]+$/.test(backend)) {
    return Response.json({ error: "SERVICE_NOT_CONFIGURED" }, { status: 503 });
  }
  if (["POST", "PUT", "DELETE"].includes(req.method)) {
    const origin = req.headers.get("origin");
    if (!origin || origin !== new URL(req.url).origin) {
      return Response.json({ error: "CROSS_ORIGIN_REQUEST" }, { status: 403 });
    }
  }
  const provider = await getToken({
    req,
    secret,
    secureCookie: new URL(req.url).protocol === "https:",
  });
  if (!provider || typeof provider.apiBearer !== "string" ||
      typeof provider.apiBearerExpiry !== "number" ||
      provider.apiBearerExpiry < Math.floor(Date.now() / 1000) + 20) {
    return Response.json({ error: "SIGN_IN_REQUIRED" }, { status: 401 });
  }
  const url = backend + "/api/v1/" + endpoint.path;
  const headers = new Headers({
    Authorization: "Bearer " + provider.apiBearer,
    Accept: "application/json",
  });
  let payload: Uint8Array<ArrayBuffer> | undefined;
  if (req.method === "POST" || req.method === "PUT") {
    const type = req.headers.get("content-type")?.split(";")[0] ?? "";
    const image = req.method === "POST";
    if (image && !["image/jpeg", "image/png", "image/webp"].includes(type)) {
      return Response.json({ error: "INVALID_IMAGE_TYPE" }, { status: 415 });
    }
    if (!image && type !== "application/json") {
      return Response.json({ error: "INVALID_CONTENT_TYPE" }, { status: 415 });
    }
    const reader = req.body?.getReader();
    if (!reader) return Response.json({ error: "EMPTY_REQUEST" }, { status: 400 });
    const chunks: Uint8Array[] = [];
    let total = 0;
    const maximum = image ? MAX_IMAGE_BYTES : 2000;
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        total += value.length;
        if (total > maximum) {
          await reader.cancel();
          return Response.json({ error: "PAYLOAD_TOO_LARGE" }, { status: 413 });
        }
        chunks.push(value);
      }
    } finally { reader.releaseLock(); }
    payload = new Uint8Array(new ArrayBuffer(total));
    let offset = 0;
    for (const chunk of chunks) { payload.set(chunk, offset); offset += chunk.length; }
    headers.set("Content-Type", type);
  }

  try {
    const response = await fetch(url, {
      method: req.method,
      headers,
      body: payload,
      cache: "no-store",
      signal: AbortSignal.timeout(20000),
    });
    const bytes = await response.arrayBuffer();
    if (bytes.byteLength > 1_000_000) {
      return Response.json({ error: "BACKEND_RESPONSE_TOO_LARGE" }, { status: 502 });
    }
    return new Response(bytes, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("content-type") || "application/json",
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      },
    });
  } catch {
    return Response.json({ error: "BACKEND_UNAVAILABLE" }, { status: 503 });
  }
}

export async function GET(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return forward(req, ctx);
}
export async function PUT(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return forward(req, ctx);
}
export async function POST(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return forward(req, ctx);
}
export async function DELETE(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return forward(req, ctx);
}
