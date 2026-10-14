import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="header">
      <div className="container header-inner">
        <Link href="/" className="logo" aria-label="DermaLens AI home">
          <span className="logo-mark" aria-hidden="true">✳</span>
          DermaLens <span className="logo-accent">AI</span>
        </Link>
        <nav aria-label="Primary navigation" className="nav">
          <Link href="/check">Image check</Link>
          <Link href="/how-it-works">How it works</Link>
          <Link href="/privacy">Privacy</Link>
          <Link href="/assistant">Assistant</Link>
        </nav>
        <Link className="button button-small button-outline" href="/check">Get started <span aria-hidden>↗</span></Link>
      </div>
    </header>
  );
}
