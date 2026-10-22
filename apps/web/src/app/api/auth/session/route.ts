import { NextRequest, NextResponse } from "next/server";
import { getAuthConfig, readSession, verifiedAccount } from "@/lib/auth-server";

export async function GET(request: NextRequest) {
  try {
    const config = getAuthConfig();
    const session = readSession(request, config);
    if (!session) return NextResponse.json({ authenticated: false }, { headers: { "Cache-Control": "no-store" } });
    const result = await verifiedAccount(config, session.token);
    if (result.status === 401 || result.status === 403) {
      return NextResponse.json({ authenticated: false }, { headers: { "Cache-Control": "no-store" } });
    }
    if (!result.ok) throw new Error("Account API unavailable");
    return NextResponse.json({ authenticated: true }, { headers: { "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json({ authenticated: false, error: "Sign-in service unavailable." }, { status: 503 });
  }
}
