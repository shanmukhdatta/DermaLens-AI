import { describe, expect, it } from "vitest";
import { parseFeedbackInput, validFeedbackResponse } from "./research-feedback";

describe("Protected feedback contracts", () => {
  it("accepts only exact allowlisted choice objects", () => {
    expect(parseFeedbackInput({ choice: "unsure" })).toBe("unsure");
    expect(parseFeedbackInput({ choice: "incorrect" })).toBe("incorrect");
    expect(parseFeedbackInput({ choice: "diagnose" })).toBeNull();
    expect(parseFeedbackInput({ choice: "correct", account_id: "someone-else" })).toBeNull();
    expect(parseFeedbackInput(null)).toBeNull();
    expect(parseFeedbackInput(["correct"])).toBeNull();
  });
  it("verifies server feedback shape", () => {
    expect(validFeedbackResponse({ id: "abc", choice: "quality_issue", review_status: "pending" })).toBe(true);
    expect(validFeedbackResponse({ id: "abc", choice: "fake", review_status: "pending" })).toBe(false);
    expect(validFeedbackResponse({ id: "", choice: "correct", review_status: "pending" })).toBe(false);
  });
});
