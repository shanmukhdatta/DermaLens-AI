import type { Metadata } from "next";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "DermaLens AI | Facial Skin Research Engineering", template: "%s | DermaLens AI" },
  description: "Explore privacy-first facial image quality checks, six-class skin research architecture, explainable AI experiments and reproducible engineering. Model inference is not yet connected; not a medical diagnostic service.",
  robots: { index: true, follow: true },
  openGraph: {
    title: "DermaLens AI — Facial Skin Research Engineering",
    description: "An open-source engineering showcase for computer vision, model provenance and privacy-first image research. No clinical diagnosis.",
    type: "website",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en"><body><SiteHeader /><div id="main-content" tabIndex={-1}>{children}</div><SiteFooter /></body></html>
  );
}
