import { NextRequest, NextResponse } from "next/server";
import { getAuthConfig, readSession, sameOrigin } from "@/lib/auth-server";

type Context = { params: Promise<{ action?: string[] }> };
const MAX_UPLOAD = 8 * 1024 * 1024;
const ID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** Owner-only, explicit BFF proxy; bearer tokens never reach browser JavaScript. */
async function forward(request: NextRequest, context: Context, method: "POST" | "GET" | "DELETE") {
  let config;
  try { config = getAuthConfig(); }
  catch { return NextResponse.json({ error: "Research account service unavailable." }, { status: 503 }); }

  const parts = (await context.params).action || [];
  const id = parts.length === 1 && ID.test(parts[0]) ? parts[0] : null;
  if ((method === "POST" && parts.length !== 0) || (method !== "POST" && id === null)) {
    return NextResponse.json({ error: "Not found." }, { status: 404 });
  }
  if (method !== "GET" && !sameOrigin(request, config)) {
    return NextResponse.json({ error: "Forbidden." }, { status: 403 });
  }
  const session = readSession(request, config);
  if (!session) return NextResponse.json({ error: "Sign-in required." }, { status: 401 });
  let payload: Uint8Array<ArrayBuffer> | undefined;
  let contentType: string | undefined;

  if (method === "POST") {
    contentType = request.headers.get("content-type")?.split(";")[0].trim().toLowerCase();
    if (!contentType || !["image/jpeg", "image/png", "image/webp"].includes(contentType)) {
      return NextResponse.json({ error: "Expected a supported image." }, { status: 415 });
    }
    const length = Number(request.headers.get("content-length") || "0");
    if (!Number.isFinite(length) || length > MAX_UPLOAD) {
      return NextResponse.json({ error: "Image exceeds 8 MB." }, { status: 413 });
    }
    const reader = request.body?.getReader();
    if (!reader) return NextResponse.json({ error: "Image required." }, { status: 422 });
    const chunks: Uint8Array[] = [];
    let total = 0;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > MAX_UPLOAD) {
        await reader.cancel();
        return NextResponse.json({ error: "Image exceeds 8 MB." }, { status: 413 });
      }
      chunks.push(value);
    }
    if (total === 0) return NextResponse.json({ error: "Image required." }, { status: 422 });
    payload = new Uint8Array(new ArrayBuffer(total));
    let position = 0;
    for (const part of chunks) { payload.set(part, position); position += part.byteLength; }
  }

  try {
    const upstream = await fetch(
      config.apiBase + "/api/v1/analyses" + (id ? "/" + id : ""),
      {
        method,
        headers: {
          Authorization: "Bearer " + session.token,
          ...(contentType ? { "Content-Type": contentType } : {}),
        },
        ...(payload ? { body: payload } : {}),
        cache: "no-store",
        signal: AbortSignal.timeout(90_000),
      },
    );
    return new NextResponse(upstream.status === 204 ? null : await upstream.text(), {
      status: upstream.status,
      headers: {
        "Cache-Control": "no-store",
        ...(upstream.status === 204 ? {} : { "Content-Type": "application/json" }),
      },
    });
  } catch {
    return NextResponse.json({ error: "Experimental analysis service unavailable." }, { status: 503 });
  }
}

export async function POST(request: NextRequest, context: Context) {
  return forward(request, context, "POST");
}
export async function GET(request: NextRequest, context: Context) {
  return forward(request, context, "GET");
}
export async function DELETE(request: NextRequest, context: Context) {
  return forward(request, context, "DELETE");
}
