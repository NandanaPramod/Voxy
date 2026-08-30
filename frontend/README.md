# Voxy — Frontend

React + Vite + JavaScript frontend for **Voxy**, the AI-powered scam call
detection hackathon MVP. This is `Voxy/frontend/` in the team monorepo.

Owned by: Frontend role (branch: `frontend`).
Scope: this folder only. Do not modify `backend/` or `ml/`.

## Stack

- React 18 + Vite
- JavaScript only (no TypeScript)
- Tailwind CSS
- framer-motion (animations/transitions)
- lucide-react (icons)

## Run locally

```sh
npm install
npm run dev
```

## Flow

```text
Home → Upload Audio → Analyze → Loading/Analyzing → Results Dashboard
```

State machine lives in `src/App.jsx`.

## Backend connection

`src/lib/api.js` currently returns mock data (`src/lib/mockResult.js`) so the
UI works without the backend. The mock result matches the team's agreed
JSON contract exactly:

```json
{
  "transcript": "...",
  "voice_risk": 72,
  "scam_risk": 90,
  "overall_risk": 82,
  "risk_level": "CRITICAL",
  "threats": ["Bank Impersonation", "OTP Request", "Urgency"],
  "recommended_action": "...",
  "ledger_status": "Recorded"
}
```

Once the backend's `POST /analyze` is live, set `USE_MOCK = false` in
`src/lib/api.js` and update `BACKEND_URL` if needed. No other frontend
changes should be required.

## Structure

```text
frontend/
├── src/
│   ├── pages/         Home, UploadPage, AnalyzingPage, ResultsPage
│   ├── components/    Header, Footer, Logo, StepIndicator, FileDrop,
│   │                  RiskGauge, RiskMeter, ThreatList, WaveformVisual
│   ├── lib/           api.js, mockResult.js, riskConfig.js
│   ├── App.jsx        step state machine
│   └── main.jsx       entry point
├── index.html
├── tailwind.config.js
└── vite.config.js
```

## Notes

This project started from a "Lovable" landing-page template. It has been
stripped down to only what Voxy's flow needs — see the team channel /
CHANGES.md for what was removed and why.
