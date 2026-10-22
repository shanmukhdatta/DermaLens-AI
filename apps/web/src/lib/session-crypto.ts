import { createCipheriv, createDecipheriv, randomBytes, timingSafeEqual } from "node:crypto";

/** Short-lived, authenticated encrypted browser cookie; no plaintext bearer tokens. */
export function sealCookie(data: unknown, purpose: string, secretHex: string): string {
  if (!/^[a-fA-F0-9]{64}$/.test(secretHex)) throw new Error("Invalid session encryption key");
  const iv = randomBytes(12);
  const cipher = createCipheriv("aes-256-gcm", Buffer.from(secretHex, "hex"), iv);
  cipher.setAAD(Buffer.from("dermalens:" + purpose));
  const plaintext = Buffer.from(JSON.stringify(data), "utf8");
  const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  return Buffer.concat([iv, cipher.getAuthTag(), ciphertext]).toString("base64url");
}

export function openCookie(value: string | undefined, purpose: string, secretHex: string): unknown {
  if (!value || value.length > 8192 || !/^[a-fA-F0-9]{64}$/.test(secretHex)) return null;
  try {
    const bytes = Buffer.from(value, "base64url");
    if (bytes.length < 29) return null;
    const decipher = createDecipheriv("aes-256-gcm", Buffer.from(secretHex, "hex"), bytes.subarray(0, 12));
    decipher.setAAD(Buffer.from("dermalens:" + purpose));
    decipher.setAuthTag(bytes.subarray(12, 28));
    return JSON.parse(Buffer.concat([decipher.update(bytes.subarray(28)), decipher.final()]).toString("utf8")) as unknown;
  } catch {
    return null;
  }
}

export function constantTimeEqual(left: string, right: string): boolean {
  const a = Buffer.from(left);
  const b = Buffer.from(right);
  return a.length === b.length && timingSafeEqual(a, b);
}
