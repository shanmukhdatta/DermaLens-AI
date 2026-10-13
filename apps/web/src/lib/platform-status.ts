export type PlatformStatus = Readonly<{
  ready: false;
  title: string;
  description: string;
}>;

export const platformStatus: PlatformStatus = Object.freeze({
  ready: false,
  title: "Model analysis unavailable",
  description:
    "This release contains the frontend and API engineering foundation only. Image upload, prediction and chatbot features are not enabled.",
});
