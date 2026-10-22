import { identity } from "@/auth";
import type { NextRequest } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Fail closed without a configured OIDC provider and session secret.
export async function GET(req: NextRequest) {
  return identity ? identity.handlers.GET(req) :
    Response.json({ error: "IDENTITY_PROVIDER_NOT_CONFIGURED" }, { status: 503 });
}

export async function POST(req: NextRequest) {
  return identity ? identity.handlers.POST(req) :
    Response.json({ error: "IDENTITY_PROVIDER_NOT_CONFIGURED" }, { status: 503 });
}
