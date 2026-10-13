import { describe, expect, it } from "vitest";

import { platformStatus } from "./platform-status";

describe("research-only status", () => {
  it("never claims that inference is ready", () => {
    expect(platformStatus.ready).toBe(false);
    expect(platformStatus.title).toBe("Model analysis unavailable");
  });

  it("clearly explains the unavailable capabilities", () => {
    expect(platformStatus.description).toContain("not enabled");
    expect(platformStatus.description).toContain("prediction");
  });
});
