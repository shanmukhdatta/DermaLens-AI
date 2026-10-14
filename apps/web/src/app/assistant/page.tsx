import Link from "next/link";

export default function AssistantPage() {
  return <main className="container page-container narrow"><div className="page-intro"><span className="eyebrow">Project documentation</span><h1>Documentation assistant</h1><p>The documentation-grounded assistant is being integrated. It will answer questions about the architecture, pipeline and limitations using approved project documents. It will not diagnose skin conditions or provide treatment advice.</p><div className="notice notice-neutral"><strong>Not connected yet</strong><p>No language-model service is being called from this page. We will enable chat only after retrieval and source-grounding tests pass.</p></div><Link href="/how-it-works" className="button button-primary">Learn how DermaLens works →</Link></div></main>;
}
