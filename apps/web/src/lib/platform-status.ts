export type PlatformStatus = Readonly<{ ready: false; title: string; description: string }>;

export const platformStatus: PlatformStatus = Object.freeze({
  ready: false,
  title: "Model analysis unavailable",
  description: "Skin prediction and diagnostic capabilities are not enabled. An independent image suitability check is available only when the API operator enables it.",
});
