# Harness Continual Learning

**Continual Adaptation Beyond Model Parameters**

This repository hosts the static research project website. The page preserves the v10 design, the original manuscript figures, selected experimental results, and two reserved Minecraft comparison-video slots.

- Repository: https://github.com/boringKey/Harness-Continual-Learning
- Target project-page URL: https://boringkey.github.io/Harness-Continual-Learning/
- arXiv: https://arxiv.org/abs/2608.19013

The project-page URL becomes available after the site files have been uploaded and GitHub Pages has deployed successfully. This repository is the website source; it does not by itself indicate a release of the research implementation.

## Publish

1. Upload the contents of the prepared `Harness-Continual-Learning` folder to the repository root. `index.html` and `static/` must be directly at the root, not inside another nested folder. Do not upload the ZIP itself.
2. In **Settings → Pages → Build and deployment**, select **Deploy from a branch**, **main**, and **/(root)**, then save.
3. Check the Pages deployment in **Actions**. Use the **Visit site** link in Pages settings after a successful deployment.

The `.nojekyll` file is intentionally present. No Node.js, npm, or frontend build step is required.

For detailed instructions, see [DEPLOY.zh-CN.md](DEPLOY.zh-CN.md) after uploading the full site package.

## Local preview

```bash
python3 scripts/check_site.py
python3 -m http.server 8000
```

Open `http://localhost:8000` on your own computer.

## Add the Minecraft videos

Put the recordings in `static/videos/` and edit `src`, `title`, and `caption` in `static/js/config.js`. Paths are relative to `index.html`, for example `static/videos/comparison-1.mp4`, without a leading slash. Leave `src` empty until the recording is available.

Keep your existing video configuration and recordings when replacing website files. `codeUrl` is reserved for the actual research-code URL; `websiteRepository` points to this project-page repository.

## Sources and licensing

The source manuscript and figure provenance are documented in `SOURCES.md` and `static/data/figure-provenance.json`. See `LICENSE` for the webpage-code and research-asset terms.
