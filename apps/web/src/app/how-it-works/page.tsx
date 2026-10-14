import Link from "next/link";

const modules = [
  ["01", "Input protection", "File-size limits, supported formats, safe decoding and basic image quality."],
  ["02", "Face suitability", "A replaceable face detector checks for an appropriate single-face image."],
  ["03", "Research classifier", "A separate, versioned Keras model adapter. Not available until checkpoint and validation gates pass."],
  ["04", "Uncertainty first", "Future calibration and unknown-input tests determine when the classifier should abstain."],
  ["05", "Transparent feedback", "Opt-in history and reviewed corrections, never automatic changes to the live model."],
  ["06", "Documentation assistant", "A project-documentation-only RAG assistant; not a medical advice chatbot."],
];

export default function HowItWorksPage() {
  return (
    <main className="container page-container">
      <div className="page-intro"><span className="eyebrow">Behind the technology</span><h1>A responsible pipeline, step by step.</h1><p>Each module has a specific job and must pass its own acceptance tests before being enabled.</p></div>
      <div className="card-grid two">
        {modules.map(([index, name, description]) => <article className="feature-card" key={index}><span className="step-number">{index}</span><h2>{name}</h2><p>{description}</p></article>)}
      </div>
      <section className="callout-section"><h2>Why we don't show skin diagnoses yet</h2><p>The research models were trained using synthetic and real image data. Clinical reliability, real-camera generalization and class-specific failure rates still require independent validation. Even a high model score does not guarantee a diagnosis.</p><Link className="button button-primary" href="/check">Try image checks →</Link></section>
    </main>
  );
}
