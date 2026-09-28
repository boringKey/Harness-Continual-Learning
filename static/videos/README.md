# Comparison videos

No real recordings have been supplied. The two placeholders are intentional.

Add `comparison-1.mp4` and `comparison-2.mp4`, then edit `../js/config.js`:

- `src`: `static/videos/comparison-1.mp4` (relative to `index.html`)
- `title` and `caption`: describe what the recording actually shows
- `poster`: optional image
- `captions`: optional WebVTT track

Do not remove existing recordings during website updates. The player uses native controls and `playsinline`, without forced autoplay. The site also handles an unavailable media URL gracefully.
