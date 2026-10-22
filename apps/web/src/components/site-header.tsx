"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { href: "/check", label: "Image check" },
  { href: "/how-it-works", label: "How it works" },
  { href: "/privacy", label: "Privacy" },
  { href: "/assistant", label: "Assistant" },
  { href: "/research", label: "Research" },
  { href: "/history", label: "My history" },
] as const;

export function SiteHeader() {
  const pathname = usePathname();
  return (
    <header className="header">
      <a className="skip-link" href="#main-content">Skip to content</a>
      <div className="container header-inner">
        <Link href="/" className="logo" aria-label="DermaLens AI home">
          <span className="logo-mark" aria-hidden="true">✳</span>
          DermaLens <span className="logo-accent">AI</span>
        </Link>
        <nav aria-label="Primary navigation" className="nav">
          {navigation.map(({ href, label }) => (
            <Link key={href} href={href} aria-current={pathname === href ? "page" : undefined}>
              {label}
            </Link>
          ))}
        </nav>
        <Link className="button button-small button-outline" href="/check">
          Get started <span aria-hidden="true">↗</span>
        </Link>
      </div>
    </header>
  );
}
