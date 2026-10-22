import type { Metadata } from "next";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { ResearchAuthProvider } from "@/components/research-auth-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "DermaLens AI | Responsible Image Analysis Research",
  description: "An engineering research prototype for private image suitability checks and explainable AI system design.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <ResearchAuthProvider>
          <SiteHeader />
          <div id="main-content" tabIndex={-1}>{children}</div>
          <SiteFooter />
        </ResearchAuthProvider>
      </body>
    </html>
  );
}
