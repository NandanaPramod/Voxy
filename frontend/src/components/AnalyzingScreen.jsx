// ============================================================
// AnalyzingScreen.jsx
// Shown while we "wait" for analysis to finish. Cycles through
// text describing each stage of the pipeline (matches the
// team's architecture: speech -> scam detection -> voice -> risk).
//
// Props:
//   fileName — name of the file being analyzed, just for display
// ============================================================

import { useEffect, useState } from 'react'
import './AnalyzingScreen.css'

const STAGES = [
  'Transcribing audio…',
  'Scanning conversation for scam patterns…',
  'Checking voice authenticity…',
  'Calculating overall risk…',
]

export default function AnalyzingScreen({ fileName }) {
  const [stageIndex, setStageIndex] = useState(0)

  useEffect(() => {
    // Move to the next stage text every 800ms, looping back at the end.
    const interval = setInterval(() => {
      setStageIndex((i) => (i + 1) % STAGES.length)
    }, 800)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="page analyzing-page">
      <div className="scan-rings" aria-hidden="true">
        <span className="scan-ring scan-ring-1" />
        <span className="scan-ring scan-ring-2" />
        <span className="scan-ring scan-ring-3" />
        <div className="scan-core">
          <PulseIcon />
        </div>
      </div>

      <h2 className="analyzing-title">Analyzing call…</h2>
      {fileName && <p className="analyzing-file">{fileName}</p>}

      <p className="analyzing-stage" key={stageIndex}>
        {STAGES[stageIndex]}
      </p>

      <div className="stage-dots">
        {STAGES.map((_, i) => (
          <span key={i} className={`stage-dot ${i === stageIndex ? 'stage-dot-active' : ''}`} />
        ))}
      </div>
    </div>
  )
}

function PulseIcon() {
  return (
    <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
      <path
        d="M2 12h4l2 7 4-14 2 7h8"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
