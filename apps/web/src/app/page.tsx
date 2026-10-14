import Link from "next/link";
import { platformStatus } from "@/lib/platform-status";

const steps = [
  { number: "01", title: "Choose a photo", description: "Select a face photo from your device. No image is retained by default." },
  { number: "02", title: "Check suitability", description: "The application validates format, size and basic face visibility." },
  { number: "03", title: "Review limitations", description: "See a transparent quality report, including uncertainty and recapture guidance." },
];

export default function HomePage() {
  return (
    <main>
      <section className="hero container">
        <div className="hero-copy">
          <span className="eyebrow">Responsible AI · Computer vision research</span>
          <h1>Understand the <em>image.</em> Respect the <em>uncertainty.</em></h1>
          <p className="lead">
            DermaLens AI brings image quality, privacy and careful machine-learning engineering
            together in one approachable experience.
          </p>
          <div className="button-group">
            <Link className="button button-primary" href="/check">Check an image <span aria-hidden>↗</span></Link>
            <Link className="button button-outline" href="/how-it-works">Explore the technology</Link>
          </div>
          <p className="disclaimer-inline">Research prototype only. Never use results to diagnose or rule out a skin condition.</p>
        </div>
        <div className="hero-visual" aria-hidden="true">
          <div className="visual-ring ring-one" />
          <div className="visual-ring ring-two" />
          <div className="visual-skin-card">
            <span className="visual-eyebrow">DERMALENS / IMAGE PIPELINE</span>
            <div className="face-outline">
              <div className="face-top" />
              <span className="face-eye eye-left" />
              <span className="face-eye eye-right" />
              <span className="face-nose" />
              <span className="face-mouth" />
            </div>
            <div className="visual-metric"><span className="metric-dot" /> Privacy-first processing</div>
          </div>
          <div className="floating-card floating-one">Image suitability <span>↗</span></div>
          <div className="floating-card floating-two">Model status <strong>Unavailable</strong></div>
        </div>
      </section>

      <section className="soft-section">
        <div className="container">
          <div className="section-heading">
            <span className="eyebrow">How the prototype works</span>
            <h2>Careful checks before any model result.</h2>
            <p>The engineering workflow makes image limitations visible instead of hiding them.</p>
          </div>
          <div className="card-grid three">
            {steps.map((step) => (
              <article className="feature-card" key={step.number}>
                <span className="step-number">{step.number}</span>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="container two-column-section">
        <div>
          <span className="eyebrow">Current capabilities</span>
          <h2>Built with boundaries you can see.</h2>
          <p className="muted">We separate photo suitability checks from actual skin classification. Only a verified, independently evaluated model can enable inference.</p>
          <Link href="/privacy" className="text-link">Read our privacy approach →</Link>
        </div>
        <div className="status-panel" role="status">
          <span className="status-label">CURRENT MODEL STATUS</span>
          <h3>{platformStatus.title}</h3>
          <p>{platformStatus.description}</p>
          <div className="status-foot"><span className="status-indicator" /> Research development mode</div>
        </div>
      </section>
    </main>
  );
}
