import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
const style = readFileSync(new URL("../app/globals.css", import.meta.url), "utf8");
describe("DermaLens accessible green-and-white design", () => {
  it("uses the agreed green accents with readable contrast on light backgrounds", () => {
    expect(style).toContain("--accent: #198565");
    expect(style).toContain("--accent-dark: #075c43");
    expect(style).toContain("background: #f8fcfa");
  });
  it("supports keyboard navigation, current page and reduced motion", () => {
    expect(style).toContain(".skip-link:focus");
    expect(style).toContain('a[aria-current="page"]');
    expect(style).toContain("prefers-reduced-motion: reduce");
  });
});
