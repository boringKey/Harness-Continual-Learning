# Validation — v10

The adjacent `browser-report.json` and `static-report.txt` record checks actually run on this revision.

## Completed

- Static verification of links, anchors, figure provenance, manuscript hash, selected results, baselines, bar lengths, absolute gains, forgetting/action labels and complete CSV/JSON archives.
- Minecraft-specific demo heading and description; removal of the three paper deep links; both figure enlargement controls remain.
- Eleven Chromium viewport widths: 320, 360, 375, 390, 620, 720, 721, 768, 820, 1024 and 1440 CSS pixels. No document or tested-component horizontal overflow was found.
- Both original figures open at 3184px; fit/original-size toggle, Escape, close button, caption enlargement and focus return.
- Citation-button response, creation of top-level embedded-PDF Blob URLs, content visible without JavaScript.
- Editable video title/caption and code link; synthetic media-error placeholder; rejection of javascript: URLs.
- Manual visual review of rendered video, overview and results sections.

## Limitations

Screenshots were rendered from portable HTML with embedded local assets. Chromium blocked an attempt to open the local HTTP site with ERR_BLOCKED_BY_ADMINISTRATOR; local HTTP loading is **not tested** and is not presented as a pass. This restriction was not overridden.

No real recordings have been supplied; synthetic error events are not playback tests. OS clipboard contents were not independently read. PDF link creation was checked, but PDF viewer navigation was not independently automated. No live GitHub changes, Pages deployment, external-link check or Safari/Firefox test is claimed.
