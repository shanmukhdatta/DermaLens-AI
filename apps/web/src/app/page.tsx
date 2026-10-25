import Link from "next/link";
import { platformStatus } from "@/lib/platform-status";

const conditions = ["Acne", "Fungal infection", "Hyperpigmentation", "Normal skin", "Skin cancer", "Vitiligo"];
const capabilities = [
  { symbol: "◉", title: "Image quality gateway", description: "Check file safety, brightness and basic face visibility before any analysis. This is the public demo." },
  { symbol: "▦", title: "Research-ready inference", description: "Versioned Keras model contracts, exact label maps and reproducibility checks. Trained weights are not installed." },
  { symbol: "◎", title: "Explainability & uncertainty", description: "Offline Grad-CAM and calibration research modules with explicit abstention boundaries." },
  { symbol: "↗", title: "Private by design", description: "No raw-photo retention in the image check. Owner-scoped history and feedback require verified sign-in." },
  { symbol: "⌘", title: "Documentation explorer", description: "Search curated architecture and privacy documents with citations, without inventing clinical answers." },
  { symbol: "◫", title: "Engineering reproducibility", description: "FastAPI, Next.js, PostgreSQL, Docker, model manifest validation and continuous integration." },
];

export default function HomePage() {
  return (
    <main>
      <section className="hero container">
        <div className="hero-copy">
          <span className="eyebrow">DERMALENS AI · COMPUTER VISION RESEARCH</span>
          <h1>Skin research, built with <em>clarity.</em></h1>
          <p className="lead">Explore an end-to-end facial image AI engineering platform: safe image checks, versioned model interfaces, explainability research and a transparent path to deployment.</p>
          <div className="hero-points"><span>Six research classes</span><span>Privacy-first</span><span>Open source</span></div>
          <div className="button-group">
            <Link className="button button-primary" href="/check">Try the image check <span aria-hidden="true">↗</span></Link>
            <Link className="button button-outline" href="/how-it-works">See how it works</Link>
          </div>
          <div className="prototype-banner" role="note">
            <span aria-hidden="true">ⓘ</span>
            <span><strong>Research prototype · Model not connected</strong>Photo quality checks are separate from disease classification. The six-class predictor is disabled pending verified weights and independent validation. This is not a medical diagnostic service.</span>
          </div>
        </div>
        <div className="hero-visual" aria-label="Illustration of the proposed image-processing pipeline">
          <div className="visual-ring ring-one" aria-hidden="true" />
          <div className="visual-ring ring-two" aria-hidden="true" />
          <div className="visual-skin-card product-visual">
            <div className="product-topline"><span>DERMALENS / PIPELINE</span><span className="product-chip">Research v1</span></div>
            <div className="visual-steps">
              <div className="visual-step"><span>01</span> Image upload & consent</div>
              <div className="pipeline-divider">↓</div>
              <div className="visual-step"><span>02</span> Quality + one-face checks</div>
              <div className="pipeline-divider">↓</div>
              <div className="visual-step muted"><span>03</span> Six-class research model · pending</div>
              <div className="pipeline-divider">↓</div>
              <div className="visual-step muted"><span>04</span> Reliability & XAI · pending</div>
            </div>
            <div className="visual-metric"><span className="metric-dot" /> Source code available · clinical analysis off</div>
          </div>
          <div className="floating-card floating-one">Modular architecture <span>✓</span></div>
          <div className="floating-card floating-two">Inference status <strong>Not connected</strong></div>
        </div>
      </section>

      <section className="soft-section">
        <div className="container">
          <div className="section-heading">
            <span className="eyebrow">Research scope</span>
            <h2>Six categories. One explainable engineering workflow.</h2>
            <p>The original research project defines these classes. Showing them here does not mean that live classification, subtype detection or severity grading is available.</p>
          </div>
          <div className="classes-grid">{conditions.map((name, i) => (
            <article className="class-tile" key={name}><span>CLASS {String(i + 1).padStart(2, "0")}</span><strong>{name}</strong></article>
          ))}</div>
          <div className="section-actions"><span className="status-note">◌ &nbsp; Classification unavailable in the public demo</span><Link className="text-link" href="/research">See research evaluation tools →</Link></div>
        </div>
      </section>

      <section className="container two-column-section">
        <div>
          <span className="eyebrow">Current capabilities</span>
          <h2>Show the engineering. State the limits.</h2>
          <p className="muted">Visitors can explore the image quality workflow, documentation, architecture and browser-local aggregate research reports. Verified model weights, clinically evaluated probabilities and patient-grade interpretations are not offered.</p>
          <div className="technical-strip"><span>Next.js</span><span>FastAPI</span><span>TensorFlow / Keras</span><span>PostgreSQL</span><span>Docker</span><span>CI/CD</span></div>
          <div className="section-actions"><Link className="text-link" href="/how-it-works">Read the technical pipeline →</Link></div>
        </div>
        <div className="status-panel" role="status"><span className="status-label">MODEL READINESS</span><h3>{platformStatus.title}</h3><p>{platformStatus.description}</p><div className="status-foot"><span className="status-indicator" /> Deployment-safe: inference disabled</div></div>
      </section>

      <section className="soft-section">
        <div className="container">
          <div className="section-heading"><span className="eyebrow">Platform features</span><h2>Built as a system, not just a model.</h2><p>Each module has a distinct responsibility, test boundary and integration contract.</p></div>
          <div className="card-grid three">{capabilities.map((capability) => (
            <article className="feature-card" key={capability.title}><span className="feature-symbol" aria-hidden="true">{capability.symbol}</span><h3>{capability.title}</h3><p>{capability.description}</p></article>
          ))}</div>
        </div>
      </section>

      <section className="container centered-footer-cta">
        <span className="eyebrow">Explore the project</span>
        <h2>See what works today, and what comes next.</h2>
        <p>Try the photo suitability check when the backend is online, read the architecture, or review the open-source implementation. No fabricated demo predictions.</p>
        <div className="button-group"><Link className="button button-primary" href="/check">Open image check</Link><a className="button button-outline" target="_blank" rel="noopener noreferrer" href="https://github.com/shanmukhdatta/DermaLens-AI">View GitHub source ↗</a></div>
      </section>
    </main>
  );
}
