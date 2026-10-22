import { NextResponse } from "next/server";
import { cookieName, cookieOptions, discover, getAuthConfig, newAuthorization, transactionCookie } from "@/lib/auth-server";

export async function GET() {
  try {
    const config = getAuthConfig();
    const metadata = await discover(config);
    const flow = newAuthorization(config, metadata.authorization_endpoint);
    const response = NextResponse.redirect(flow.target);
    response.cookies.set(cookieName("transaction", config),
      transactionCookie(config, flow.state, flow.verifier), cookieOptions(config, 600));
    response.headers.set("Cache-Control", "no-store");
    return response;
  } catch {
    return NextResponse.json({ error: "Verified sign-in is not available in this deployment." }, { status: 503 });
  }
}
