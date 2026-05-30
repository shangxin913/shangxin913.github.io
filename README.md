# TikTok Daily Account Monitor

Static dashboard for daily TikTok account monitoring.

The main page is `index.html`. It is designed for GitHub Pages, Vercel, Netlify, or any static hosting service.

Tracked accounts are listed in `window.MONITOR_ACCOUNTS`. Daily check results are stored in `window.MONITOR_ENTRIES` between:

```js
// CODEX_MONITOR_DATA_START
// CODEX_MONITOR_DATA_END
```

The Codex automation updates that data block after each daily run.
