/** Research feedback is not a verified clinical diagnosis or label. */
export const FEEDBACK_CHOICES = [
  { value: "correct", label: "Matches my understanding" },
  { value: "incorrect", label: "Does not match my understanding" },
  { value: "unsure", label: "Unsure / cannot assess" },
  { value: "quality_issue", label: "Photo or output quality issue" },
] as const;

export type FeedbackChoice = (typeof FEEDBACK_CHOICES)[number]["value"];
export type ResearchFeedback = {
  id: string;
  choice: FeedbackChoice;
  review_status: string;
};

export function parseFeedbackInput(value: unknown): FeedbackChoice | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const keys = Object.keys(value);
  if (keys.length !== 1 || keys[0] !== "choice") return null;
  const choice = (value as Record<string, unknown>).choice;
  return typeof choice === "string" && FEEDBACK_CHOICES.some(item => item.value === choice)
    ? choice as FeedbackChoice
    : null;
}

export function validFeedbackResponse(value: unknown): value is ResearchFeedback {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const obj = value as Record<string, unknown>;
  return typeof obj.id === "string" && obj.id.length > 0 &&
    typeof obj.review_status === "string" &&
    parseFeedbackInput({ choice: obj.choice }) !== null;
}
