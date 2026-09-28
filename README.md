# Harness Continual Learning

**Continual Adaptation Beyond Model Parameters**

This repository contains the research project website, the author-supplied manuscript, original figures, selected results, and two reserved Minecraft comparison-video slots. This is the website source, not a claim that the research implementation has been released.

**Project website (after Pages deployment):** https://boringkey.github.io/Harness-Continual-Learning/

**Paper on arXiv:** https://arxiv.org/abs/2608.19013

## Publish

Upload `index.html`, `static/`, and the other package contents directly to the repository root. Do not upload the ZIP or a nested parent directory. Then select **Settings → Pages → Deploy from a branch → main → /(root)** and save. Verify the deployment in Actions before sharing the website URL.

For the complete instructions and the 404 diagnosis, see [DEPLOY.zh-CN.md](DEPLOY.zh-CN.md).

Alternatively, use the included publisher on your computer with Python 3.9+ and the GitHub CLI:

```bash
gh auth login --hostname github.com --web
python3 scripts/publish_pages.py
```

The script publishes only to `boringKey/Harness-Continual-Learning`, never force-pushes, preserves remote-only files and existing video configuration, and verifies the live page and key assets. It does not modify your personal-homepage repository. It asks for confirmation before writing.

## Local preview

```bash
python3 scripts/check_site.py
python3 -m http.server 8000
```

Open `http://localhost:8000` locally. The deployment uses relative asset links so the project subpath works.

## Videos and sources

Edit `static/js/config.js` to configure the two recordings. Empty sources intentionally remain placeholders. Preserve your existing configuration and recordings when replacing website files.

See `SOURCES.md`, `static/data/figure-provenance.json`, and `LICENSE` for research sources, original-figure provenance, and licensing.
