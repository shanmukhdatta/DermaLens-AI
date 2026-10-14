import Link from "next/link";

export default function HistoryPage() {
  return <main className="container page-container narrow"><div className="page-intro"><span className="eyebrow">Your history</span><h1>History is currently unavailable.</h1><p>Personal history requires verified sign-in, consent and an operational database. We will not show fabricated past analyses or accept unverified account identifiers.</p><Link href="/privacy" className="button button-outline">Review our privacy approach</Link></div></main>;
}
