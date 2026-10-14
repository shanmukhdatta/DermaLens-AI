"use client";

import { ChangeEvent, useEffect, useRef, useState } from "react";
import { checkImageQuality, friendlyReason, ImageCheckError, QualityReport, validateImageFile } from "@/lib/image-api";

export default function CheckPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [consent, setConsent] = useState(false);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<QualityReport | null>(null);
  const abort = useRef<AbortController | null>(null);

  useEffect(() => () => {
    if (preview) URL.revokeObjectURL(preview);
    abort.current?.abort();
  }, [preview]);

  function chooseFile(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.currentTarget.files?.[0] ?? null;
    abort.current?.abort();
    setReport(null);
    setError(null);
    setFile(null);
    setPreview(null);
    setWorking(false);
    setConsent(false);
    if (!selected) return;
    const validation = validateImageFile(selected);
    if (validation) {
      setError(validation);
      return;
    }
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
  }

  async function runCheck() {
    if (!file || !consent || working) return;
    setWorking(true);
    setError(null);
    setReport(null);
    const controller = new AbortController();
    abort.current = controller;
    try {
      const result = await checkImageQuality(file, controller.signal);
      if (!controller.signal.aborted) setReport(result);
    } catch (reason) {
      if (!controller.signal.aborted) {
        setError(reason instanceof ImageCheckError ? reason.message : "Unable to check this image.");
      }
    } finally {
      if (!controller.signal.aborted) setWorking(false);
    }
  }

  return (
    <main className="container page-container">
      <div className="page-intro">
        <span className="eyebrow">Image suitability · Step 01</span>
        <h1>Check your image.</h1>
        <p>Upload one face photo to test whether it meets basic image-quality requirements. This is not a skin diagnosis.</p>
      </div>
      <div className="workspace">
        <section className="upload-panel" aria-labelledby="upload-title">
          <div className="panel-heading">
            <span className="panel-icon" aria-hidden="true">▣</span>
            <div><h2 id="upload-title">Your photograph</h2><p>JPEG, PNG or WebP · Maximum 8 MB</p></div>
          </div>
          <label className="upload-drop">
            {preview ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={preview} alt="Preview of the selected photograph" className="image-preview" />
            ) : (
              <span className="upload-empty"><span className="upload-glyph" aria-hidden="true">↑</span><strong>Choose a face photograph</strong><span>Click to browse or take a photograph</span></span>
            )}
            <input type="file" accept="image/jpeg,image/png,image/webp" capture="user" onChange={chooseFile} aria-label="Choose a face photograph" />
          </label>
          {file && <p className="file-caption">Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</p>}
          <label className="consent-row">
            <input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} />
            <span>I understand this image is sent to the configured quality-check service for immediate processing. It is not stored by this workflow.</span>
          </label>
          <button type="button" className="button button-primary button-full" disabled={!file || !consent || working} onClick={runCheck}>
            {working ? "Checking image…" : "Run image quality check"} <span aria-hidden="true">↗</span>
          </button>
          <p className="microcopy">No account is required for this check. Avoid uploading another person&apos;s photograph without permission.</p>
        </section>
        <section className="result-panel" aria-labelledby="result-title" aria-live="polite">
          <div className="panel-heading"><span className="panel-icon muted-icon" aria-hidden="true">◎</span><div><h2 id="result-title">Quality report</h2><p>Transparent engineering checks</p></div></div>
          {!report && !error && !working && (
            <div className="empty-results"><div className="large-glyph" aria-hidden="true">◇</div><h3>Ready when you are</h3><p>Select an image, review the notice and run the check to see the result here.</p></div>
          )}
          {working && <div className="empty-results" role="status"><div className="loading-spinner" /><h3>Inspecting image</h3><p>Validating format and checking face visibility.</p></div>}
          {error && <div className="notice notice-error" role="alert"><strong>Could not complete the check</strong><p>{error}</p></div>}
          {report && (
            <div className="report">
              <div className={report.accepted ? "notice notice-ok" : "notice notice-warn"}>
                <strong>{report.accepted ? "Image suitability check passed" : "Please choose a different photo"}</strong>
                <p>{report.accepted ? "This image meets the enabled basic quality gates. No skin condition was assessed." : "The image did not meet the current face visibility checks."}</p>
              </div>
              <div className="report-metrics"><div><span>Dimensions</span><strong>{report.width} × {report.height}</strong></div><div><span>Faces found</span><strong>{report.face_count ?? "—"}</strong></div></div>
              {[...report.reasons, ...report.warnings].length > 0 && (
                <div className="report-advice"><h3>Quality guidance</h3><ul>{[...report.reasons, ...report.warnings].map((code) => <li key={code}>{friendlyReason(code)}</li>)}</ul></div>
              )}
              <div className="notice notice-neutral"><strong>No medical analysis performed</strong><p>{report.notice}</p></div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
