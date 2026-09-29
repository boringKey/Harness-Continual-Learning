/* Minecraft demo configuration. Local paths are relative to index.html.
 * The descriptions refer to the author-supplied DeepSeek V4.1 Flash / Max
 * video comparison; they do not replace the separate manuscript results.
 */
window.HCL_CONFIG = {
  "websiteRepository": "https://github.com/boringKey/Harness-Continual-Learning",
  "codeUrl": "",
  "videos": [
    {
      "id": "comparison-1",
      "title": "Zero-shot",
      "caption": "DeepSeek V4.1 Flash (reasoning effort: Max) fails at task 22, “Mine 3 coal,” and cannot proceed to subsequent tasks.",
      "src": "static/videos/minecraft-zero-shot.mp4",
      "poster": "",
      "captions": "",
      "captionLanguage": "en"
    },
    {
      "id": "comparison-2",
      "title": "HCL",
      "caption": "With Harness Continual Learning (HCL), the same model and reasoning effort successfully complete task 22, where the zero-shot run failed, and continue through the remaining tasks, ultimately completing all 50 tasks.",
      "src": "static/videos/minecraft-hcl.mp4",
      "poster": "",
      "captions": "",
      "captionLanguage": "en"
    }
  ]
};
