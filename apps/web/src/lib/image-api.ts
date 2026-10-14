export const MAX_UPLOAD_BYTES = 8 * 1024 * 1024;
export const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"] as const;

export type QualityReport = Readonly<{
  accepted: boolean;
  reasons: string[];
  warnings: string[];
  width: number | null;
  height: number | null;
  face_count: number | null;
  blur_signal: number | null;
  brightness_signal: number | null;
  medical_analysis_available: false;
  notice: string;
}>;

export class ImageCheckError extends Error {
  constructor(message: string, readonly status?: number) {
    super(message);
    this.name = "ImageCheckError";
  }
}

export function validateImageFile(file: Pick<File, "size" | "type">): string | null {
  if (!ALLOWED_TYPES.some((type) => type === file.type)) {
    return "Choose a JPEG, PNG or WebP image.";
  }
  if (file.size === 0 || file.size > MAX_UPLOAD_BYTES) {
    return "Choose an image smaller than 8 MB.";
  }
  return null;
}

export function friendlyReason(reason: string): string {
  const descriptions: Record<string, string> = {
    NO_FACE_DETECTED: "No clearly detectable face was found. Try a front-facing photograph.",
    MULTIPLE_FACES_DETECTED: "More than one face was detected. Use an image containing one person.",
    FACE_TOO_SMALL: "Move a little closer to the camera and try again.",
    POSSIBLY_BLURRY: "The image may be blurry. Hold the camera steady in good light.",
    POSSIBLY_DARK: "The image may be too dark. Try even, natural lighting.",
    POSSIBLY_OVEREXPOSED: "The image may be overexposed. Avoid direct glare.",
  };
  return descriptions[reason] ?? "The image did not satisfy a required quality check.";
}

export async function checkImageQuality(file: File, signal?: AbortSignal): Promise<QualityReport> {
  const validationError = validateImageFile(file);
  if (validationError) throw new ImageCheckError(validationError);
  const base = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  let response: Response;
  try {
    response = await fetch(base + "/api/v1/images/check", {
      method: "POST",
      body: file,
      headers: { "Content-Type": file.type },
      cache: "no-store",
      signal,
    });
  } catch {
    throw new ImageCheckError("Unable to reach the image-check service. Please try again later.");
  }
  if (!response.ok) {
    if (response.status === 503) {
      throw new ImageCheckError("The image-check service is not enabled in this deployment.", 503);
    }
    if (response.status === 413) throw new ImageCheckError("The image is too large.", 413);
    if (response.status === 415 || response.status === 422) {
      throw new ImageCheckError("The image could not be read. Choose another photograph.", response.status);
    }
    throw new ImageCheckError("The service could not process this request.", response.status);
  }
  const value: unknown = await response.json().catch(() => null);
  if (!value || typeof value !== "object" || !("accepted" in value) || !("reasons" in value)
    || typeof value.accepted !== "boolean" || !Array.isArray(value.reasons)
    || !("medical_analysis_available" in value) || value.medical_analysis_available !== false) {
    throw new ImageCheckError("The server returned an unexpected response.");
  }
  return value as QualityReport;
}
