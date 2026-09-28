/* Edit this file to add the two comparison videos and the research-code link.
 * All local paths are relative to index.html, NOT to this config.js file.
 * Leave src empty until a real video is available. No fake video is shipped.
 * A direct HTTPS .mp4 URL also works. A YouTube watch-page URL is not an MP4.
 */
window.HCL_CONFIG = {
  // This is the website repository, not a claim that research code is released.
  websiteRepository: "https://github.com/boringKey/Harness-Continual-Learning",
  // Set this only after the actual research-code repository is available.
  codeUrl: "",
  videos: [
    {
      id: "comparison-1",
      title: "Comparison 1",
      caption: "A comparison recording will be added here.",
      src: "", // e.g. "static/videos/comparison-1.mp4"
      poster: "", // optional: "static/images/comparison-1.jpg"
      captions: "", // optional WebVTT: "static/videos/comparison-1.en.vtt"
      captionLanguage: "en"
    },
    {
      id: "comparison-2",
      title: "Comparison 2",
      caption: "A comparison recording will be added here.",
      src: "", // e.g. "static/videos/comparison-2.mp4"
      poster: "",
      captions: "",
      captionLanguage: "en"
    }
  ]
};
