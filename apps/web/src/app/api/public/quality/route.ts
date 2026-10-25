import { NextRequest, NextResponse } from "next/server";
import { getBackendOrigin } from "@/lib/backend-origin";

export const runtime = "nodejs";
const MAX_UPLOAD_BYTES = 8 * 1024 * 1024;
const TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

function message(reason: string, code: number) {
  return NextResponse.json({ error: reason }, { status: code, headers: { "Cache-Control": "no-store" } });
}

/** Bounded same-origin proxy. No photo logging, caching, disk persistence or medical inference. */
export async function POST(request: NextRequest) {
  const origin = getBackendOrigin();
  if (!origin) return message("Image check backend is not configured for this deployment.", 503);

  const mime = request.headers.get("content-type")?.split(";")[0]?.toLowerCase().trim() || "";
  if (!TYPES.has(mime)) return message("Unsupported image type.", 415);
  const lengthHeader = request.headers.get("content-length");
  if (lengthHeader) {
    const length = Number(lengthHeader);
    if (!Number.isSafeInteger(length) || length <= 0 || length > MAX_UPLOAD_BYTES) {
      return message("Image size is not supported.", 413);
    }
  }
  const reader = request.body?.getReader();
  if (!reader) return message("An image is required.", 400);
  const chunks: Uint8Array[] = [];
  let total = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > MAX_UPLOAD_BYTES) {
        await reader.cancel().catch(() => undefined);
        return message("Image is larger than 8 MB.", 413);
      }
      chunks.push(value);
    }
    if (total === 0) return message("An image is required.", 400);
    const combined = new Uint8Array(total);
    let offset = 0;
    for (const chunk of chunks) { combined.set(chunk, offset); offset += chunk.byteLength; }

    const upstream = await fetch(origin + "/api/v1/images/check", {
      method: "POST",
      headers: { "Content-Type": mime },
      body: new Blob([combined], { type: mime }),
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(15000),
    });
    const responseText = await upstream.text();
    if (responseText.length > 32768) return message("Unexpected response from image-check backend.", 502);
    const content = upstream.headers.get("content-type") || "";
    if (!content.includes("application/json")) return message("Unexpected backend response.", 502);
    return new Response(responseText, {
      status: upstream.status,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" },
    });
  } catch {
    return message("Image-check backend is unavailable.", 503);
  }
}
