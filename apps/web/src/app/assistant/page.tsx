"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { DocumentationSearch, searchProjectDocs, validateDocsQuestion } from "@/lib/docs-api";

const EXAMPLES = [
  "What preprocessing does the model expect?",
  "How does image quality checking work?",
  "How is research feedback handled?",
];

export default function AssistantPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<DocumentationSearch | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [working, setWorking] = useState(false);
  const abort = useRef<AbortController | null>(null);

  useEffect(() => () => abort.current?.abort(), []);

  async function ask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (working) return;
    const issue = validateDocsQuestion(question);
    if (issue) { setError(issue); return; }
    abort.current?.abort();
    const controller = new AbortController();
    abort.current = controller;
    setWorking(true);
    setError(null);
    setAnswer(null);
    try {
      const result = await searchProjectDocs(question, controller.signal);
      if (!controller.signal.aborted) setAnswer(result);
    } catch (cause) {
      if (!controller.signal.aborted) {
        setError(cause instanceof Error ? cause.message : "Search is unavailable.");
      }
    } finally {
      if (!controller.signal.aborted) setWorking(false);
    }
  }

  return (
    <main className="container page-container narrow">
      <div className="page-intro">
        <span className="eyebrow">Documentation explorer</span>
        <h1>Ask about the DermaLens project.</h1>
        <p>Search approved project documents for explanations of our technology, privacy and limitations.</p>
        <p className="disclaimer-inline">This is cited document search, not a live Grok chat or AI medical advice.</p>
      </div>
      <section className="workspace docs-workspace" aria-label="Documentation search">
        <div className="upload-panel">
          <h2>Search project documentation</h2>
          <form onSubmit={ask}>
            <label className="docs-label" htmlFor="docs-question">Your technical question</label>
            <textarea className="docs-textarea" id="docs-question" value={question}
              onChange={event => setQuestion(event.target.value)}
              maxLength={180} rows={4} placeholder="How is the facial image processed?" />
            <button className="button button-primary button-full" disabled={working} type="submit">
              {working ? "Searching documents…" : "Find documented answers"}
            </button>
          </form>
          <p className="microcopy">Do not enter personal or medical information.</p>
          <div className="docs-examples">
            {EXAMPLES.map(example => (
              <button type="button" key={example} onClick={() => setQuestion(example)}>
                {example}
              </button>
            ))}
          </div>
        </div>
        <div className="result-panel" aria-live="polite">
          <h2>Sources</h2>
          {error && <div className="notice notice-error" role="alert">{error}</div>}
          {!error && !answer && <p className="muted">
            {working ? "Retrieving relevant documentation…" : "Matching passages will appear with their sources."}
          </p>}
          {answer && answer.matches.length === 0 && <div className="notice notice-neutral">
            No relevant passages found. Try a question about architecture or preprocessing.
          </div>}
          {answer && answer.matches.map((match, i) => (
            <article className="docs-match" key={match.path + i}>
              <strong>{match.section}</strong>
              <p>{match.excerpt}</p>
              <small>Source: {match.path}</small>
            </article>
          ))}
          {answer && <p className="microcopy">{answer.notice}</p>}
        </div>
      </section>
      <p className="microcopy">You can also <Link href="/how-it-works">read how DermaLens works.</Link></p>
    </main>
  );
}
