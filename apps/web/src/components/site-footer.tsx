import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <p>© DermaLens AI · Research engineering prototype. Not a diagnostic device.</p>
        <div>
          <Link href="/privacy">Privacy</Link>
          <Link href="/how-it-works">Method</Link>
          <a href="https://github.com/shanmukhdatta/DermaLens-AI" target="_blank" rel="noopener noreferrer">Source ↗</a>
        </div>
      </div>
    </footer>
  );
}
