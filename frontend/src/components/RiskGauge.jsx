// ============================================================
// RiskGauge.jsx
// The signature visual of the results page: a circular gauge
// (like a speedometer bent into a ring) that fills up to match
// overall_risk (0-100), colored by risk_level.
//
// Props:
//   score      — number 0-100 (overall_risk)
//   level      — string, e.g. "CRITICAL" (risk_level)
//   theme      — { color, bg, label } from riskTheme.js
// ============================================================

import { useEffect, useState } from 'react'

const SIZE = 200
const STROKE = 14
const RADIUS = (SIZE - STROKE) / 2
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

export default function RiskGauge({ score, theme }) {
  // Animate the number counting up and the ring filling in,
  // instead of just snapping to the final value.
  const [displayScore, setDisplayScore] = useState(0)

  useEffect(() => {
    let frame
    const duration = 900
    const start = performance.now()

    function tick(now) {
      const progress = Math.min((now - start) / duration, 1)
      // ease-out so it settles gently instead of stopping abruptly
      const eased = 1 - Math.pow(1 - progress, 3)
      setDisplayScore(Math.round(eased * score))
      if (progress < 1) frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [score])

  const offset = CIRCUMFERENCE * (1 - displayScore / 100)

  return (
    <div className="risk-gauge">
      <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`}>
        {/* Track (the full grey ring behind the colored progress) */}
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke="var(--glass-border)"
          strokeWidth={STROKE}
        />
        {/* Progress arc */}
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke={theme.color}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${SIZE / 2} ${SIZE / 2})`}
          style={{
            transition: 'stroke 0.3s ease',
            filter: `drop-shadow(0 0 10px ${theme.color})`,
          }}
        />
      </svg>

      <div className="risk-gauge-center">
        <span className="risk-gauge-score">{displayScore}</span>
        <span className="risk-gauge-max">/ 100</span>
      </div>
    </div>
  )
}
