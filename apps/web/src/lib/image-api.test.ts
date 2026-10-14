import { describe, expect, it } from "vitest";
import { friendlyReason, MAX_UPLOAD_BYTES, validateImageFile } from "./image-api";

describe("image upload client guardrails", () => {
  it("rejects unsupported and oversized uploads", () => {
    expect(validateImageFile({ size: 500, type: "text/plain" })).toContain("JPEG");
    expect(validateImageFile({ size: 0, type: "image/jpeg" })).toContain("smaller");
    expect(validateImageFile({ size: MAX_UPLOAD_BYTES + 1, type: "image/png" })).toContain("smaller");
    expect(validateImageFile({ size: 512, type: "image/webp" })).toBeNull();
  });
  it("turns stable face gate codes into human guidance", () => {
    expect(friendlyReason("NO_FACE_DETECTED")).toContain("face");
    expect(friendlyReason("UNKNOWN")).toContain("quality");
  });
});
