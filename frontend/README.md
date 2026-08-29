# Voxy — Frontend

This is the `frontend/` module for the Voxy hackathon project, built with
**React + Vite + plain JavaScript/CSS** (no TypeScript, no extra libraries).

It currently runs on **mock data** (see `src/data/mockResult.js`) so it works
fully on its own, without the backend running.

## What's inside

```text
src/
├── main.jsx                      entry point, do not usually need to touch
├── App.jsx                       controls which screen shows (home/analyzing/results)
├── App.css                       shared layout styles
├── index.css                     design tokens (colors, fonts) — the theme lives here
├── data/
│   ├── mockResult.js             fake analysis result, matches the backend's JSON contract
│   └── riskTheme.js              maps risk_level ("CRITICAL" etc.) to colors
└── components/
    ├── HomePage.jsx / .css       landing page + audio upload dropzone
    ├── AnalyzingScreen.jsx / .css   loading animation while "analyzing"
    ├── ResultsDashboard.jsx / .css  the full risk report
    └── RiskGauge.jsx             the animated circular risk score gauge
```

## Run it locally

You need [Node.js](https://nodejs.org) installed (v18 or newer). Then, inside
the `frontend/` folder:

```bash
npm install
npm run dev
```

Open the URL it prints (usually `http://localhost:5173`) in your browser.

- Drop any audio file onto the upload box, click **Analyze Call**, and it will
  show a ~3-second fake loading animation, then the results dashboard with
  mock data.
- Refreshing or clicking **Analyze Another Call** takes you back to the start.

To build the production version:

```bash
npm run build
```

This creates a `dist/` folder with the final, optimized site.

## Connecting to the real backend (once it's ready)

Open `src/App.jsx` and find the `handleAnalyze` function. There is a clearly
commented block titled **BACKEND HAND-OFF POINT**. Replace the `setTimeout`
mock block with a real `fetch('http://localhost:8000/analyze', ...)` call —
the exact code to paste is already written in the comment right above it.

Nothing else needs to change: `ResultsDashboard.jsx` reads the response using
the exact field names from the integration contract
(`transcript`, `voice_risk`, `scam_risk`, `overall_risk`, `risk_level`,
`threats`, `recommended_action`, `ledger_status`), so as long as the backend
returns that shape, the UI will just work with real data instead of mock data.

## Design notes

- Dark, glass-panel look with an indigo/cyan brand accent, and a separate
  red → orange → amber → green color scale used only for risk levels, so
  "danger" never gets confused with "brand color."
- The circular gauge on the results page is the one signature visual element;
  everything else stays quiet and functional on purpose.
- Everything is responsive down to small phone widths, and all interactive
  elements have visible keyboard focus rings.
