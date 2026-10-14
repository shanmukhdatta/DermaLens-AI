import { describe, expect, it } from "vitest";
import { validateDocsQuestion } from "./docs-api";

describe("documentation lookup input", () => {
  it("rejects empty or unbounded queries", () => {
    expect(validateDocsQuestion("  ")).toBeTruthy();
    expect(validateDocsQuestion("a".repeat(181))).toBeTruthy();
    expect(validateDocsQuestion("model preprocessing")).toBeNull();
  });
});
