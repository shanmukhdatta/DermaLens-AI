import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DermaLens AI | Research Engineering Foundation",
  description: "Research-only platform architecture. Image analysis is not available.",
  robots: { index: false, follow: false },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
