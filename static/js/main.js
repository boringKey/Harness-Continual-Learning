/* Progressive enhancement: all research content remains readable without JavaScript. */
(() => {
  "use strict";
  document.documentElement.classList.add("js");
  const config = window.HCL_CONFIG || {};

  /** Permit ordinary local asset paths and HTTP(S) URLs, but never executable URL schemes. */
  function safeAssetUrl(value) {
    if (typeof value !== "string" || !value.trim()) return "";
    const input = value.trim();
    if (/^(?:https?:)?\/\//i.test(input)) {
      try {
        const resolved = new URL(input, document.baseURI);
        return ["http:", "https:"].includes(resolved.protocol) ? resolved.href : "";
      } catch (_) { return ""; }
    }
    return !/^[a-z][a-z0-9+.-]*:/i.test(input) && !/[\u0000-\u001f]/.test(input) ? input : "";
  }
  function safeExternalUrl(value) {
    if (typeof value !== "string" || !/^https?:\/\//i.test(value.trim())) return "";
    return safeAssetUrl(value);
  }

  // Distinguish research code from the source of this project website.
  const codeUrl = safeExternalUrl(config.codeUrl);
  const codeResource = document.getElementById("code-resource");
  if (codeUrl && codeResource) {
    const link = document.createElement("a");
    link.className = "button";
    link.href = codeUrl;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    const icon = codeResource.querySelector("svg");
    if (icon) link.append(icon.cloneNode(true));
    link.append(document.createTextNode(" Code"));
    codeResource.replaceChildren(link);
  }
  const websiteLink = document.getElementById("website-source");
  const repositoryUrl = safeExternalUrl(config.websiteRepository);
  if (repositoryUrl && websiteLink) websiteLink.href = repositoryUrl;

  // Empty slots do not request a missing video. Configured videos retain native accessible controls.
  for (const entry of Array.isArray(config.videos) ? config.videos : []) {
    if (!entry || typeof entry.id !== "string") continue;
    const card = document.getElementById(entry.id);
    if (!card || !card.classList.contains("video-card")) continue;
    const video = card.querySelector("video");
    const placeholder = card.querySelector(".video-placeholder");
    const title = card.querySelector(".video-title");
    const caption = card.querySelector(".video-caption");
    if (typeof entry.title === "string" && entry.title.trim()) {
      title.textContent = entry.title;
      video.setAttribute("aria-label", entry.title);
    }
    if (typeof entry.caption === "string") caption.textContent = entry.caption;
    const src = safeAssetUrl(entry.src);
    if (!src) continue;
    const poster = safeAssetUrl(entry.poster);
    if (poster) video.poster = poster;
    const captions = safeAssetUrl(entry.captions);
    if (captions) {
      video.crossOrigin = "anonymous";
      const track = document.createElement("track");
      track.kind = "captions";
      track.src = captions;
      track.srclang = typeof entry.captionLanguage === "string" ? entry.captionLanguage : "en";
      track.label = track.srclang;
      video.append(track);
    }
    video.addEventListener("error", () => {
      video.hidden = true;
      placeholder.hidden = false;
      placeholder.querySelector(".placeholder-label").textContent = "Video unavailable";
      let detail = placeholder.querySelector(".placeholder-detail");
      if (!detail) {
        detail = document.createElement("span");
        detail.className = "placeholder-detail";
        placeholder.append(detail);
      }
      detail.textContent = "The recording could not be loaded. Please try again later.";
    });
    video.src = src;
    video.hidden = false;
    placeholder.hidden = true;
  }

  // Paper figures are original images. Links remain usable when dialogs/JS are unavailable.
  const dialog = document.getElementById("figure-dialog");
  const dialogImage = document.getElementById("dialog-image");
  const dialogTitle = document.getElementById("figure-dialog-title");
  const originalLink = document.getElementById("figure-original");
  const fitButton = document.getElementById("figure-fit");
  if (dialog && typeof dialog.showModal === "function") {
    let trigger = null;
    document.querySelectorAll("[data-figure]").forEach(link => {
      link.addEventListener("click", event => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        trigger = link;
        dialogImage.src = link.href;
        dialogImage.alt = link.dataset.figure;
        dialogTitle.textContent = link.dataset.figure;
        originalLink.href = link.href;
        dialog.classList.remove("zoomed");
        fitButton.textContent = "Original size";
        document.body.classList.add("has-dialog");
        dialog.showModal();
      });
    });
    document.getElementById("figure-close").addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });
    dialog.addEventListener("close", () => {
      document.body.classList.remove("has-dialog");
      if (trigger) trigger.focus({preventScroll: true});
    });
    fitButton.addEventListener("click", () => {
      const zoomed = dialog.classList.toggle("zoomed");
      fitButton.textContent = zoomed ? "Fit to window" : "Original size";
    });
  }

  // Copy with a graceful fallback for local file previews and older browsers.
  const copyButton = document.getElementById("copy-bibtex");
  const bibtex = document.getElementById("bibtex-code");
  const status = document.getElementById("copy-status");
  let resetTimer;
  if (copyButton && bibtex && status) {
    copyButton.addEventListener("click", async () => {
      let copied = false;
      if (navigator.clipboard && window.isSecureContext) {
        try { await navigator.clipboard.writeText(bibtex.textContent); copied = true; } catch (_) { /* Selection fallback below. */ }
      }
      if (!copied) {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(bibtex);
        selection.removeAllRanges();
        selection.addRange(range);
        try { copied = document.execCommand("copy"); } catch (_) { copied = false; }
        if (copied) selection.removeAllRanges();
      }
      status.textContent = copied ? "BibTeX copied to clipboard." : "Citation selected. Press Ctrl+C or ⌘C to copy.";
      const label = copyButton.querySelector("span");
      if (label) label.textContent = copied ? "Copied" : "Selected";
      window.clearTimeout(resetTimer);
      resetTimer = window.setTimeout(() => { if (label) label.textContent = "Copy citation"; }, 2500);
    });
  }
})();
