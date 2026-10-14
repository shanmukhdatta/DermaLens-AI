/** Parse aggregate, research-only evaluations locally without uploading or storing data. */

export type EvaluationCategory = Readonly<{
  label: string;
  support: number;
  precision: number;
  recall: number;
  f1: number;
}>;

export type ResearchEvaluation = Readonly<{
  modelVersion: string;
  evaluated: number;
  subjects: number;
  accuracy: number;
  macroF1: number;
  calibrationError: number;
  categories: EvaluationCategory[];
  warnings: string[];
}>;

const LABELS = ["Acne", "Fungal Infection", "Hyperpigmentation", "Normal Skin", "Skin Cancer", "Vitiligo"];

function record(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Invalid evaluation report.");
  return value as Record<string, unknown>;
}

function boundedNumber(value: unknown, key: string): number {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 1) {
    throw new Error("Invalid evaluation metric: " + key);
  }
  return value;
}

export function parseResearchEvaluation(source: string): ResearchEvaluation {
  if (source.length > 512 * 1024) throw new Error("Evaluation file exceeds 512 KB.");
  let decoded: unknown;
  try { decoded = JSON.parse(source); } catch { throw new Error("This is not valid JSON."); }
  const input = record(decoded);
  if (input.report_type !== "research_evaluation_only" || input.clinical_use_validated !== false) {
    throw new Error("Only nonclinical DermaLens research evaluation reports are supported.");
  }
  if (typeof input.model_version !== "string" || !input.model_version.trim()
    || input.model_version.length > 90) throw new Error("Invalid model identity.");
  const metrics = record(input.metrics);
  const n = metrics.n;
  const subjects = input.held_out_subject_groups;
  if (!Number.isSafeInteger(n) || typeof n !== "number" || n < 1
    || !Number.isSafeInteger(subjects) || typeof subjects !== "number" || subjects < 1) {
    throw new Error("Invalid held-out sample count.");
  }
  const perClass = record(metrics.per_class);
  if (Object.keys(perClass).length !== 6) throw new Error("Expected six trained research categories.");
  const categories = LABELS.map(label => {
    const key = Object.keys(perClass).find(name => name.replaceAll("_", " ").toLowerCase() === label.toLowerCase());
    if (!key) throw new Error("Missing trained research category.");
    const item = record(perClass[key]);
    if (typeof item.support !== "number" || !Number.isSafeInteger(item.support)
      || item.support < 0 || item.support > n) throw new Error("Invalid category support.");
    return {
      label,
      support: item.support,
      precision: boundedNumber(item.precision, "precision"),
      recall: boundedNumber(item.recall, "recall"),
      f1: boundedNumber(item.f1, "f1"),
    };
  });
  if (categories.reduce((sum, row) => sum + row.support, 0) !== n) {
    throw new Error("Category counts do not match held-out total.");
  }
  const warnings = Array.isArray(input.warnings)
    ? input.warnings.filter((w): w is string => typeof w === "string").slice(0, 8).map(w => w.slice(0, 200))
    : [];
  return {
    modelVersion: input.model_version,
    evaluated: n,
    subjects,
    accuracy: boundedNumber(metrics.accuracy, "accuracy"),
    macroF1: boundedNumber(metrics.macro_f1, "macro_f1"),
    calibrationError: boundedNumber(metrics.ece_10_bins_exploratory, "ece"),
    categories,
    warnings,
  };
}
