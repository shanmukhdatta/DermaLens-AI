"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useResearchAuth } from "@/components/research-auth-provider";

export default function AuthCallbackPage() {
  const [problem, setProblem] = useState<string | null>(null);
  const started = useRef(false);
  const router = useRouter();
  const { completeRedirect } = useResearchAuth();

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    completeRedirect().then(() => router.replace("/history")).catch((cause: unknown) => {
      setProblem(cause instanceof Error ? cause.message : "Unable to complete sign-in.");
    });
  }, [completeRedirect, router]);

  return (
    <main className="container page-container narrow">
      <div className="page-intro">
        <span className="eyebrow">Protected research session</span>
        <h1>{problem ? "Sign-in unavailable" : "Completing sign-in"}</h1>
        {problem ? <p role="alert">{problem}</p> :
          <p role="status">Checking the identity provider and backend permission…</p>}
        <a className="button button-outline" href="/history">Back to research history</a>
      </div>
    </main>
  );
}
