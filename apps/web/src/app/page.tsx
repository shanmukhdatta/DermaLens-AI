import { platformStatus } from "@/lib/platform-status";

export default function HomePage() {
  return (
    <main className="shell">
      <header className="topbar">
        <span className="brand">DermaLens <span className="brand-accent">AI</span></span>
        <span className="phase-pill">Phase 1 · Foundation</span>
      </header>
      <section className="hero" aria-labelledby="intro-title">
        <p className="eyebrow">Responsible computer vision engineering</p>
        <h1 id="intro-title">Building a safer foundation for image analysis.</h1>
        <p className="lead">
          DermaLens AI is an engineering research prototype for exploring facial
          skin-image classification. It is not a medical diagnostic device.
        </p>
        <div className="state" role="status" aria-live="polite">
          <span className="state-dot" aria-hidden="true" />
          <div>
            <strong>{platformStatus.title}</strong>
            <p>{platformStatus.description}</p>
          </div>
        </div>
      </section>
      <section className="details" aria-label="Project scope">
        <article className="detail">
          <h2>Privacy from the beginning</h2>
          <p>Facial-image uploads and image storage are disabled in this foundation release.</p>
        </article>
        <article className="detail">
          <h2>Verified models only</h2>
          <p>No checkpoint has been deployed; the API explicitly reports not ready.</p>
        </article>
        <article className="detail">
          <h2>Transparent limitations</h2>
          <p>No skin-condition, severity or clinical safety claims are made.</p>
        </article>
      </section>
      <footer>
        <span>For technical development and evaluation only. For skin concerns, consult a qualified healthcare professional.</span>
        <a href="https://github.com/shanmukhdatta/DermaLens-AI" rel="noopener noreferrer">
          View source on GitHub <span aria-hidden="true">↗</span>
        </a>
      </footer>
    </main>
  );
}
