import { NextRequest, NextResponse } from "next/server";
import { getBackendOrigin } from "@/lib/backend-origin";
export const runtime = "nodejs";

export async function GET(request: NextRequest) {
  const query = request.nextUrl.searchParams.get("q")?.trim() || "";
  if (query.length < 4 || query.length > 180) {
    return NextResponse.json({ error: "Enter a question between 4 and 180 characters." }, { status: 400 });
  }
  const origin = getBackendOrigin();
  if (!origin) return NextResponse.json({ error: "Documentation backend is not configured." }, { status: 503 });
  try {
    const upstream = await fetch(origin + "/api/v1/docs/search?q=" + encodeURIComponent(query), {
      method: "GET", cache: "no-store", redirect: "error", signal: AbortSignal.timeout(10000),
    });
    const text = await upstream.text();
    if (text.length > 32768 || !(upstream.headers.get("content-type") || "").includes("application/json")) {
      return NextResponse.json({ error: "Unexpected documentation backend response." }, { status: 502 });
    }
    return new Response(text, {
      status: upstream.status,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" },
    });
  } catch {
    return NextResponse.json({ error: "Documentation backend is unavailable." }, { status: 503 });
  }
}
