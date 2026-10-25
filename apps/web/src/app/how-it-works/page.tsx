import Link from "next/link";
const modules = [
  ["01", "Safe upload & image checks", "JPEG/PNG/WebP limits, bounded decoding, blur and exposure signals, and exactly one face. The image-check flow never classifies a disease.", "Demo available when API is online"],
  ["02", "Face geometry experiment", "OpenCV Haar face detection; eye-landmark orientation and conservative ROI crop as research helpers. Cropping is not enabled for serving without parity evaluation.", "Experimental"],
  ["03", "Versioned six-class inference", "Original research: full RGB image, PIL bilinear resize to 224×224, float32 [0,255], internal Keras preprocessing. The model adapter verifies private artifact manifests and output order.", "Not connected"],
  ["04", "Calibration, OOD and explanations", "Evaluate held-out calibration, unknown images, abstention thresholds and Grad-CAM before making any reliability claims. Heatmaps are not proof of disease.", "Offline research only"],
  ["05", "Accounts, feedback & audit trail", "The API supports OIDC owner authorization, encrypted metadata, consent, history, deletion and moderated research feedback. Live identity-provider integration is pending.", "Integration pending"],
  ["06", "Docs explorer, monitoring & release", "Curated documentation lookup, research metrics, CI checks, Docker deployment and model parity tooling. Vector RAG and real operations need separate verification.", "Engineering foundation"],
] as const;

export default function HowItWorksPage() {
  return (
    <main className="container page-container">
      <div className="page-intro"><span className="eyebrow">Architecture & methodology</span><h1>From a photograph to a research workflow.</h1><p>DermaLens separates image engineering, trained models, uncertainty decisions and user data. Each stage has its own contract and activation gate.</p></div>
      <div className="notice notice-neutral" role="note"><strong>No trained model connected in the public experience</strong><p>The original training and evaluation source is preserved under the research snapshot. Real inference requires a verified private model and independent performance review.</p></div>
      <div className="card-grid two">{modules.map(([number, title, description, status]) => (
        <article className="feature-card" key={number}><span className="step-number">PHASE {number} · {status}</span><h2>{title}</h2><p>{description}</p></article>
      ))}</div>
      <section className="callout-section"><h2>Why keep model analysis disabled?</h2><p>Medical-looking classifications cannot be treated as safe simply because software tests pass. We still need real checkpoint provenance, independent subject-disjoint evaluation, calibrated abstention and domain-expert review. The public demo does not diagnose or rule out skin conditions.</p><div className="button-group"><Link className="button button-primary" href="/check">Try image quality checks</Link><a className="button button-outline" href="https://github.com/shanmukhdatta/DermaLens-AI/tree/main/docs" target="_blank" rel="noopener noreferrer">Read architecture docs ↗</a></div></section>
    </main>
  );
}
