"use client";

import { ChangeEvent, useState } from "react";
import Link from "next/link";
import { parseResearchEvaluation, ResearchEvaluation } from "@/lib/research-evaluation";

function percentage(value: number) {
  return (value * 100).toFixed(1) + "%";
}

export default function ResearchPage() {
  const [report, setReport] = useState<ResearchEvaluation | null>(null);
  const [problem, setProblem] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function chooseReport(event: ChangeEvent<HTMLInputElement>) {
    const file = event.currentTarget.files?.[0] ?? null;
    setProblem(null);
    setReport(null);
    if (!file) return;
    if (file.size > 512 * 1024 || file.size === 0) {
      setProblem("Choose a research aggregate JSON report smaller than 512 KB.");
      return;
    }
    setBusy(true);
    try {
      setReport(parseResearchEvaluation(await file.text()));
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "Could not read the research report.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="container page-container">
      <div className="page-intro">
        <span className="eyebrow">Model evaluation · Research only</span>
        <h1>Examine independent test results.</h1>
        <p>Open an aggregate report created by our offline evaluation script. Files are parsed locally in your browser and are not sent to the DermaLens API.</p>
        <div className="notice notice-warn">
          <strong>Not a medical or skin diagnosis tool</strong>
          <p>These research metrics do not establish clinical safety, skin cancer screening performance, or a model&apos;s suitability for individual patients.</p>
        </div>
      </div>
      <section className="research-upload" aria-labelledby="research-title">
        <h2 id="research-title">Open a saved research summary</h2>
        <label>
          <span>Choose a non-identifying aggregate JSON report</span>
          <input type="file" accept="application/json,.json" onChange={chooseReport} aria-label="Choose research evaluation report" />
        </label>
        <p className="microcopy">Use the output of <code>scripts/evaluate_predictions.py</code>. No files are uploaded or stored by this page.</p>
      </section>
      {busy && <p role="status">Reading the report on your device…</p>}
      {problem && <div className="notice notice-error" role="alert">{problem}</div>}
      {report && (
        <section aria-labelledby="summary-title" className="research-results">
          <h2 id="summary-title">Aggregate evaluation: {report.modelVersion}</h2>
          <div className="research-metrics">
            <article><span>Held-out test images</span><strong>{report.evaluated}</strong></article>
            <article><span>Independent subject groups</span><strong>{report.subjects}</strong></article>
            <article><span>Research accuracy</span><strong>{percentage(report.accuracy)}</strong></article>
            <article><span>Research macro-F1</span><strong>{percentage(report.macroF1)}</strong></article>
            <article><span>Exploratory ECE</span><strong>{percentage(report.calibrationError)}</strong></article>
          </div>
          <h3>Per-category held-out performance</h3>
          <div className="research-scroll">
            <table>
              <thead><tr><th>Research category</th><th>Support</th><th>Precision</th><th>Recall</th><th>F1</th></tr></thead>
              <tbody>{report.categories.map(item => (
                <tr key={item.label}><th scope="row">{item.label}</th><td>{item.support}</td>
                  <td>{percentage(item.precision)}</td><td>{percentage(item.recall)}</td>
                  <td>{percentage(item.f1)}</td></tr>
              ))}</tbody>
            </table>
          </div>
          {report.warnings.length > 0 && <div className="notice notice-warn">
            <strong>Study limitations</strong>
            <ul>{report.warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul>
          </div>}
          <p className="disclaimer-inline">No category is medically validated by this visualization. This report is not a substitute for external image, label and clinical evaluation.</p>
        </section>
      )}
      <p className="microcopy">Learn about <Link href="/how-it-works">the pipeline</Link> or <Link href="/assistant">the documentation</Link>.</p>
    </main>
  );
}
