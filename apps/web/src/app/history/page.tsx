"use client";

import { ChangeEvent, useCallback, useEffect, useState } from "react";
import Link from "next/link";

import { useResearchAuth } from "@/components/research-auth-provider";
import { validateImageFile } from "@/lib/image-api";
import {
  deleteResearchResult, eraseAccount, ExperimentalResult, exportPrivateHistory,
  getAccount, getResearchResult, HistoryItem, listHistory, ResearchApiError,
  setHistoryConsent, submitResearchImage,
} from "@/lib/research-api";

export default function HistoryPage() {
  const { accessToken, configured, login, logout } = useResearchAuth();
  const [enabled, setEnabled] = useState(false);
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [selected, setSelected] = useState<ExperimentalResult | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploadAccepted, setUploadAccepted] = useState(false);
  const [busy, setBusy] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);

  const refresh = useCallback(async (token: string) => {
    const profile = await getAccount(token);
    setEnabled(profile.history_enabled);
    setItems(profile.history_enabled ? await listHistory(token) : []);
  }, []);

  useEffect(() => {
    if (!accessToken) {
      setEnabled(false); setItems([]); setSelected(null);
      return;
    }
    let alive = true;
    Promise.all([getAccount(accessToken), listHistory(accessToken)]).then(
      ([account, history]) => {
        if (alive) {
          setEnabled(account.history_enabled);
          setItems(account.history_enabled ? history : []);
        }
      },
      (error: unknown) => {
        if (alive) setProblem(error instanceof Error ? error.message : "History unavailable.");
      },
    );
    return () => { alive = false; };
  }, [accessToken]);

  async function operate(job: () => Promise<void>) {
    if (busy) return;
    setBusy(true); setProblem(null);
    try { await job(); }
    catch (error) {
      setProblem(error instanceof ResearchApiError || error instanceof Error
        ? error.message : "The operation could not be completed.");
    } finally { setBusy(false); }
  }

  function chooseFile(event: ChangeEvent<HTMLInputElement>) {
    setProblem(null); setSelected(null); setUploadAccepted(false);
    const next = event.currentTarget.files?.[0] || null;
    if (next) {
      const error = validateImageFile(next);
      if (error) { setProblem(error); setFile(null); return; }
    }
    setFile(next);
  }

  async function updateConsent(value: boolean) {
    if (!accessToken) return;
    await operate(async () => {
      const confirmed = await setHistoryConsent(accessToken, value);
      if (confirmed !== value) throw new Error("Consent update was not confirmed.");
      setEnabled(value); setSelected(null);
      await refresh(accessToken);
    });
  }

  async function submit() {
    if (!accessToken || !enabled || !file || !uploadAccepted) return;
    await operate(async () => {
      const value = await submitResearchImage(accessToken, file);
      setSelected(value); setFile(null); setUploadAccepted(false);
      await refresh(accessToken);
    });
  }

  async function showResult(id: string) {
    if (!accessToken) return;
    await operate(async () => setSelected(await getResearchResult(accessToken, id)));
  }

  async function remove(id: string) {
    if (!accessToken || !window.confirm("Delete this experimental record permanently?")) return;
    await operate(async () => {
      await deleteResearchResult(accessToken, id);
      setSelected(null);
      await refresh(accessToken);
    });
  }

  async function downloadExport() {
    if (!accessToken) return;
    await operate(async () => {
      const data = await exportPrivateHistory(accessToken);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      try {
        const link = document.createElement("a");
        link.href = url; link.download = "dermalens-private-export.json";
        document.body.appendChild(link); link.click(); link.remove();
      } finally { window.setTimeout(() => URL.revokeObjectURL(url), 1000); }
    });
  }

  async function deleteAccount() {
    if (!accessToken || !window.confirm("Delete your account and all stored research records?")) return;
    await operate(async () => {
      await eraseAccount(accessToken);
      logout();
    });
  }

  return (
    <main className="container page-container">
      <div className="page-intro">
        <span className="eyebrow">Protected research workspace</span>
        <h1>Your research history.</h1>
        <p>Only results saved with your permission appear here. Clinical interpretation is not
          available; the experimental pipeline is disabled unless a verified private model is configured.</p>
      </div>
      <div className="research-account">
        <div className="notice notice-warn">
          <strong>Not for diagnosis or skin-cancer screening</strong>
          <p>Model labels and raw scores, when available, are uncalibrated research outputs.
            Do not use them to diagnose or rule out a medical condition.</p>
        </div>
        {problem && <div role="alert" className="notice notice-error">{problem}</div>}
        {!accessToken ? (
          <section className="research-account-card">
            <h2>Sign in through your research identity provider</h2>
            <p>{configured
              ? "The external identity provider handles authentication. Access tokens stay in browser memory and expire automatically."
              : "OIDC sign-in is not configured. No demo account or fabricated history is available."}</p>
            <div className="research-actions">
              <button type="button" className="button button-primary" disabled={!configured || busy}
                onClick={() => void operate(login)}>Sign in securely</button>
              <Link href="/privacy" className="button button-outline">Privacy details</Link>
            </div>
          </section>
        ) : (
          <>
            <section className="research-account-card">
              <h2>Consent and account</h2>
              <label className="research-toggle">
                <input type="checkbox" disabled={busy} checked={enabled}
                  onChange={(event) => void updateConsent(event.target.checked)} />
                <span>Save my experimental analysis metadata for up to the configured retention period.
                  Turning this off purges saved analyses and their feedback.</span>
              </label>
              <div className="research-actions">
                <button type="button" className="button button-outline" disabled={busy}
                  onClick={() => void downloadExport()}>Export my data</button>
                <button type="button" className="button button-outline" disabled={busy}
                  onClick={logout}>Sign out locally</button>
                <button type="button" className="button button-outline" disabled={busy}
                  onClick={() => void deleteAccount()}>Delete my account</button>
              </div>
            </section>
            {enabled && (
              <section className="research-account-card research-controls">
                <h2>Experimental image analysis</h2>
                <p>Submit one face photograph only with permission. Images are processed temporarily,
                  not saved. This feature will be unavailable until a compatible verified model is configured.</p>
                <label htmlFor="research-image">Face image (JPEG, PNG, WebP; up to 8 MB)</label>
                <input id="research-image" type="file" accept="image/jpeg,image/png,image/webp"
                  onChange={chooseFile} disabled={busy} />
                <label className="research-toggle">
                  <input type="checkbox" checked={uploadAccepted}
                    onChange={event => setUploadAccepted(event.target.checked)} />
                  <span>I have permission to submit this photo and understand the result is research-only.</span>
                </label>
                <button type="button" className="button button-primary"
                  disabled={!file || !uploadAccepted || busy} onClick={() => void submit()}>
                  {busy ? "Processing request…" : "Run experimental analysis"}
                </button>
              </section>
            )}
            {selected && (
              <section className="research-account-card" aria-live="polite">
                <h2>Nonclinical research output</h2>
                <p><strong>Experimental category:</strong> {selected.research_category}</p>
                <p><strong>Uncalibrated model score:</strong> {selected.raw_model_score.toFixed(3)}</p>
                <p><strong>Model version:</strong> {selected.model.version}</p>
                <div className="notice notice-warn">{selected.notice}</div>
                <p className="microcopy">This output does not establish the presence or absence of disease.</p>
              </section>
            )}
            <section className="research-account-card">
              <h2>Stored analysis events</h2>
              {!enabled ? <p>Enable history consent to save experimental results.</p> :
                items.length === 0 ? <p>No saved analyses exist for this account.</p> :
                <div className="research-scroll">
                  <table className="research-history-table">
                    <thead><tr><th>Date</th><th>Status</th><th>Model</th><th>Actions</th></tr></thead>
                    <tbody>{items.map(item => (
                      <tr key={item.id}>
                        <td>{new Date(item.created_at).toLocaleDateString()}</td>
                        <td>{item.status}</td>
                        <td>{item.model_version ?? "—"}</td>
                        <td><div className="research-actions">
                          <button type="button" disabled={busy} onClick={() => void showResult(item.id)}>View</button>
                          <button type="button" disabled={busy} onClick={() => void remove(item.id)}>Delete</button>
                        </div></td>
                      </tr>
                    ))}</tbody>
                  </table>
                </div>}
            </section>
          </>
        )}
      </div>
    </main>
  );
}
