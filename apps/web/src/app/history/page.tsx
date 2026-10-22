"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import styles from "./history.module.css";

type Analysis = { id: string; status: string; model_version: string | null; pipeline_version: string | null; created_at: string };
type SessionState = "loading" | "signed-out" | "signed-in" | "unavailable";

export default function HistoryPage() {
  const [state, setState] = useState<SessionState>("loading");
  const [consent, setConsent] = useState(false);
  const [items, setItems] = useState<Analysis[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const refresh = useCallback(async () => {
    const [account, analyses] = await Promise.all([fetch("/api/account", { cache: "no-store" }), fetch("/api/account/analyses", { cache: "no-store" })]);
    if (!account.ok || !analyses.ok) throw new Error("Account database or verified identity is unavailable.");
    const status: { history_enabled: boolean } = await account.json();
    const history: { items: Analysis[] } = await analyses.json();
    setConsent(status.history_enabled === true);
    setItems(Array.isArray(history.items) ? history.items : []);
  }, []);
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const response = await fetch("/api/auth/session", { cache: "no-store" });
        if (!response.ok) throw new Error("Verified sign-in service is not configured or unavailable.");
        const session: { authenticated: boolean } = await response.json();
        if (cancelled) return;
        if (!session.authenticated) { setState("signed-out"); return; }
        await refresh();
        if (!cancelled) setState("signed-in");
      } catch (cause) {
        if (!cancelled) { setError(cause instanceof Error ? cause.message : "Service unavailable"); setState("unavailable"); }
      }
    })();
    return () => { cancelled = true; };
  }, [refresh]);
  async function saveConsent(enabled: boolean) {
    if (busy) return;
    setBusy(true); setError("");
    try {
      const response = await fetch("/api/account/history-consent", {
        method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ enabled }),
      });
      if (!response.ok) throw new Error("Unable to update history consent.");
      await refresh();
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Request failed."); }
    finally { setBusy(false); }
  }
  async function downloadExport() {
    setBusy(true); setError("");
    try {
      const response = await fetch("/api/account/export", { cache: "no-store" });
      if (!response.ok) throw new Error("Unable to export account records.");
      const records: unknown = await response.json();
      const url = URL.createObjectURL(new Blob([JSON.stringify(records, null, 2)], { type: "application/json" }));
      const anchor = document.createElement("a");
      anchor.href = url; anchor.download = "dermalens-account-export.json"; anchor.click();
      URL.revokeObjectURL(url);
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Export failed."); }
    finally { setBusy(false); }
  }
  async function signOut() {
    setBusy(true); setError("");
    try {
      const response = await fetch("/api/auth/logout", { method: "POST" });
      if (!response.ok) throw new Error("Could not sign out.");
      setItems([]); setConsent(false); setState("signed-out");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Sign-out failed."); }
    finally { setBusy(false); }
  }
  async function eraseAccount() {
    if (busy || !window.confirm("Permanently delete saved DermaLens account metadata and feedback? This cannot be undone.")) return;
    setBusy(true); setError("");
    try {
      const response = await fetch("/api/account", { method: "DELETE" });
      if (!response.ok) throw new Error("Unable to delete saved account data.");
      setItems([]); setConsent(false); setState("signed-out");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Deletion failed."); }
    finally { setBusy(false); }
  }
  return <main className="container page-container narrow">
    <div className="page-intro"><span className="eyebrow">Private account</span><h1>Your history and privacy.</h1>
      <p>Verified identity protects each account. No skin classification or diagnosis is performed in the current research release.</p>
    </div>
    {state === "loading" && <p role="status">Checking your session…</p>}
    {state === "unavailable" && <div className="notice notice-warn" role="alert"><strong>Account service unavailable</strong><p>{error}</p><p>Ask your deployment administrator to configure OIDC and the database.</p></div>}
    {state === "signed-out" && <section className={styles.panel}><h2>Sign in securely</h2><p>Sign-in requires an approved OpenID Connect provider. No password is collected by DermaLens.</p>
      <a href="/api/auth/login" className="button button-primary">Sign in with your provider ↗</a><p className="microcopy">Browser sessions expire automatically; medical analysis is not enabled.</p></section>}
    {state === "signed-in" && <>
      <section className={styles.panel}><div className={styles.row}><div><h2>History consent</h2><p>Save minimal analysis metadata only when explicitly enabled. Turning this off deletes saved history metadata and associated feedback.</p></div>
      <label className={styles.toggle}><input type="checkbox" checked={consent} disabled={busy} onChange={event => saveConsent(event.target.checked)} aria-label="Enable saved history" /> Enable</label></div>
      <div className={styles.actions}><button className="button button-outline" disabled={busy} onClick={downloadExport}>Export my data</button>
        <button className="button button-outline" disabled={busy} onClick={signOut}>Sign out</button></div></section>
      <section className={styles.panel}><h2>Analysis history</h2>
      {items.length === 0 ? <p>No saved analyses are available. This is expected before verified medical analysis is released.</p> :
       <ul className={styles.records}>{items.map(item => <li key={item.id}><strong>{item.status}</strong><span>{new Date(item.created_at).toLocaleDateString()}</span><span>Model: {item.model_version || "not recorded"}</span></li>)}</ul>}
      <p className="microcopy">History is limited to your verified account and only metadata is shown.</p></section>
      <section className={styles.panel}><h2>Delete saved account data</h2><p>Erase the DermaLens database account, consents, saved analysis metadata and feedback. This does not delete your external identity-provider account.</p>
        <button className="button button-outline" disabled={busy} onClick={eraseAccount}>Delete my DermaLens data</button></section>
    </>}
    {error && state !== "unavailable" && <p className="notice notice-error" role="alert">{error}</p>}
    <p><Link href="/privacy" className="text-link">Read the data and privacy approach →</Link></p>
  </main>;
}
