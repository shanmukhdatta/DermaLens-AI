import { describe, expect, it } from "vitest";
import { constantTimeEqual, openCookie, sealCookie } from "./session-crypto";

const key = "a".repeat(64);
describe("Authenticated browser session cookies", () => {
  it("round-trips and binds data to the cookie purpose", () => {
    const token = sealCookie({ state: "abc", created: 123 }, "transaction", key);
    expect(openCookie(token, "transaction", key)).toEqual({ state: "abc", created: 123 });
    expect(openCookie(token, "session", key)).toBeNull();
    expect(token).not.toContain("abc");
  });
  it("rejects tampering, a different key and malformed data", () => {
    const cookie = sealCookie({ token: "secret" }, "session", key);
    expect(openCookie(cookie, "session", "b".repeat(64))).toBeNull();
    const bytes = Buffer.from(cookie, "base64url");
    bytes[30] ^= 0xff;
    expect(openCookie(bytes.toString("base64url"), "session", key)).toBeNull();
    expect(openCookie("", "session", key)).toBeNull();
    expect(openCookie("not-cookie", "session", key)).toBeNull();
  });
  it("compares OAuth state without short-circuiting equal-sized values", () => {
    expect(constantTimeEqual("state", "state")).toBe(true);
    expect(constantTimeEqual("state", "other")).toBe(false);
    expect(constantTimeEqual("state", "s")).toBe(false);
  });
});
