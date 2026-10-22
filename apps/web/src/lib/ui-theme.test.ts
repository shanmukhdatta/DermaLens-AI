import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";

const style = readFileSync(new URL("../app/globals.css", import.meta.url), "utf8");

describe("DermaLens accessible design system", () => {
  it("uses warm orange and white with a contrast-safe primary action shade", () => {
    expect(style).toContain("--accent: #D97757");
    expect(style).toContain("--accent-dark: #9F452F");
    expect(style).toContain("background: #FAF9F6");
  });
  it("supports focus indicators, navigation state and reduced motion", () => {
    expect(style).toContain(".skip-link:focus");
    expect(style).toContain('a[aria-current="page"]');
    expect(style).toContain("prefers-reduced-motion: reduce");
  });
});
