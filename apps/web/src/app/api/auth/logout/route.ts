import { NextRequest, NextResponse } from "next/server";
import { cookieName, cookieOptions, getAuthConfig, sameOrigin } from "@/lib/auth-server";

export async function POST(request: NextRequest) {
  try {
    const config = getAuthConfig();
    if (!sameOrigin(request, config)) return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    const response = NextResponse.json({ signed_out: true });
    response.cookies.set(cookieName("session", config), "", cookieOptions(config, 0));
    response.cookies.set(cookieName("transaction", config), "", cookieOptions(config, 0));
    response.headers.set("Cache-Control", "no-store");
    return response;
  } catch {
    return NextResponse.json({ error: "Sign-out service unavailable." }, { status: 503 });
  }
}
