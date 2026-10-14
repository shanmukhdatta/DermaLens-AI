import { describe, expect, it } from "vitest";
import { parseResearchEvaluation } from "./research-evaluation";

const labels = ["Acne", "Fungal Infection", "Hyperpigmentation", "Normal Skin", "Skin Cancer", "Vitiligo"];
function fixture() {
  return {
    report_type: "research_evaluation_only",
    clinical_use_validated: false,
    model_version: "fake-fixture-not-trained",
    held_out_subject_groups: 60,
    metrics: {
      n: 60, accuracy: 0.5, macro_f1: 0.5, ece_10_bins_exploratory: 0.1,
      per_class: Object.fromEntries(labels.map(name => [name, {
        support: 10, precision: 0.5, recall: 0.5, f1: 0.5,
      }])),
    },
    warnings: ["Synthetic testing is not medical validation."],
  };
}

describe("local research summary viewer", () => {
  it("renders only bounded aggregate research measures", () => {
    const result = parseResearchEvaluation(JSON.stringify(fixture()));
    expect(result.evaluated).toBe(60);
    expect(result.categories).toHaveLength(6);
    expect(result.macroF1).toBe(0.5);
    expect(result.warnings).toHaveLength(1);
  });
  it("rejects clinical assertions and inconsistent or corrupt results", () => {
    const f = fixture();
    expect(() => parseResearchEvaluation("{}")).toThrow();
    expect(() => parseResearchEvaluation("bad")).toThrow();
    expect(() => parseResearchEvaluation(JSON.stringify({ ...f, clinical_use_validated: true }))).toThrow();
    expect(() => parseResearchEvaluation(JSON.stringify({ ...f, metrics: { ...f.metrics, n: 8 } }))).toThrow();
    expect(() => parseResearchEvaluation(JSON.stringify({ ...f, metrics: { ...f.metrics, accuracy: NaN } }))).toThrow();
  });
});
