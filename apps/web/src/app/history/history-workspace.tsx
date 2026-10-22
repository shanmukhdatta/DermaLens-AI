"use client";

import { ChangeEvent, useCallback, useEffect, useState } from "react";
import { validateImageFile } from "@/lib/image-api";

type Result = {
  id: string;
  status: string;
  created_at: string;
  expires_at?: string | null;
  medical_diagnosis: false;
  result: { reason?: string; quality?: { accepted?: boolean; reasons?: string[] } };
};
type HistoryRow = {
  id: string;
  status: string;
  created_at: string;
  model_version: string | null;
};
type History = { items: HistoryRow[] };

async function api(path: string, init?: RequestInit): Promise<unknown> {
  const response = await fetch("/api/private/" + path, {
    ...init, cache: "no-store",
  });
  if (!response.ok) throw new Error(
    response.status === 401 ? "Session expired. Sign in again." :
    response.status === 409 ? "Opt in to private history before uploading." :
    response.status === 503 ? "The private analysis service is unavailable." :
    "Request failed (" + response.status + ").",
  );
  if (response.status === 204) return null;
  return response.json();
}

export default function HistoryWorkspace() {
  const [consent, setConsent] = useState(false);
  const [rows, setRows] = useState<HistoryRow[]>([]);
  const [selected, setSelected] = useState<Result | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setError("");
    try {
      const [account, history] = await Promise.all([
        api("account") as Promise<{ history_enabled: boolean }>,
        api("account/analyses") as Promise<History>,
      ]);
      setConsent(account.history_enabled);
      setRows(history.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to read history.");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  async function optIn(enabled: boolean) {
    setBusy(true); setError("");
    try {
      await api("account/history-consent", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled }),
      });
      setConsent(enabled);
      setRows([]);
      setSelected(null);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to update privacy consent.");
    } finally { setBusy(false); }
  }

  function chooseFile(e: ChangeEvent<HTMLInputElement>) {
    const next = e.currentTarget.files?.[0] ?? null;
    if (next) {
      const invalid = validateImageFile(next);
      if (invalid) { setError(invalid); setFile(null); return; }
    }
    setFile(next); setError("");
  }

  async function analyze() {
    if (!file || !consent || busy) return;
    setBusy(true); setError("");
    try {
      const result = await api("analyses", {
        method: "POST",
        headers: { "Content-Type": file.type },
        body: file,
      }) as Result;
      setSelected(result); setFile(null); await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to create analysis.");
    } finally { setBusy(false); }
  }

  async function open(id: string) {
    setBusy(true); setError("");
    try { setSelected(await api("analyses/" + encodeURIComponent(id)) as Result); }
    catch (e) { setError(e instanceof Error ? e.message : "Unable to open result."); }
    finally { setBusy(false); }
  }

  async function erase(id: string) {
    if (busy || !window.confirm("Permanently delete this non-diagnostic analysis record?")) return;
    setBusy(true); setError("");
    try {
      await api("analyses/" + encodeURIComponent(id), { method: "DELETE" });
      if (selected?.id === id) setSelected(null);
      await refresh();
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to delete history."); }
    finally { setBusy(false); }
  }

  return <div className="workspace">
    <section className="card">
      <h2>Private consent and upload</h2>
      <p>Images are processed in memory and not saved. With consent, only the
        resulting image-quality and abstention metadata is retained for at most 30 days.</p>
      <label className="consent-row">
        <input type="checkbox" checked={consent} disabled={busy || loading}
          onChange={e => void optIn(e.target.checked)} />
        <span>Save my private non-diagnostic research history. Unchecking deletes existing records.</span>
      </label>
      {consent && <div style={{ marginTop: 20 }}>
        <input type="file" accept="image/jpeg,image/png,image/webp" onChange={chooseFile}
          aria-label="Select a face photograph for protected research checks" />
        <button className="button" disabled={!file || busy} onClick={() => void analyze()}>
          {busy ? "Processing…" : "Submit secure research check"}
        </button>
        <p className="muted">A real signed OIDC session and configured backend are required.
          Without verified model and clinical policy, the result will abstain.</p>
      </div>}
    </section>
    <section className="card">
      <h2>Stored history</h2>
      {loading ? <p>Loading your private records…</p> :
      rows.length ? <div>{rows.map(row => <div key={row.id} className="feature-card" style={{ marginBottom: 12 }}>
        <strong>{row.status}</strong>
        <p>{new Date(row.created_at).toLocaleString()}</p>
        <div style={{ display: "flex", gap: 12 }}>
          <button className="button button-outline" disabled={busy} onClick={() => void open(row.id)}>View result</button>
          <button className="button button-outline" disabled={busy} onClick={() => void erase(row.id)}>Delete</button>
        </div>
      </div>)}</div> : <p>No retained analyses for your identity.</p>}
    </section>
    {selected && <section className="card" role="status">
      <h2>Non-diagnostic result</h2>
      <p><strong>Status:</strong> {selected.status}</p>
      <p><strong>Reason:</strong> {selected.result.reason || "The model abstained or image was unsuitable."}</p>
      <p>Quality accepted: {selected.result.quality?.accepted ? "Yes" : "No / unavailable"}</p>
      <p>Expires: {selected.expires_at ? new Date(selected.expires_at).toLocaleDateString() : "Not specified"}</p>
      <p><strong>This is not a diagnosis.</strong> It does not rule out a skin condition.
        Speak with a qualified clinician if concerned.</p>
    </section>}
    {error && <p role="alert" style={{ color: "#9F452F" }}>{error}</p>}
  </div>;
}
