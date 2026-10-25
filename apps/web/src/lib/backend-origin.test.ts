import { describe, expect, it } from "vitest";
import { getBackendOrigin } from "./backend-origin";
describe("server-only backend origin", () => {
  it("disables unconfigured production forwarding", () => {
    expect(getBackendOrigin(undefined, "production")).toBeNull();
    expect(getBackendOrigin("https://api.example.org", "production")).toBe("https://api.example.org");
  });
  it("rejects insecure and ambiguous production URLs", () => {
    expect(getBackendOrigin("http://api.example.org", "production")).toBeNull();
    expect(getBackendOrigin("https://user:secret@api.example.org", "production")).toBeNull();
    expect(getBackendOrigin("https://api.example.org/private", "production")).toBeNull();
    expect(getBackendOrigin("file:///etc/passwd", "production")).toBeNull();
  });
  it("allows local development when explicitly selected", () => {
    expect(getBackendOrigin(undefined, "development")).toBe("http://127.0.0.1:8000");
  });
});
