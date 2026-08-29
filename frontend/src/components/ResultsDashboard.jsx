// ============================================================
// ResultsDashboard.jsx
// The final screen. Displays every field from the backend's
// analysis result:
//   transcript, voice_risk, scam_risk, overall_risk, risk_level,
//   threats, recommended_action, ledger_status
//
// Props:
//   result  — the analysis object (see data/mockResult.js for shape)
//   onReset — called when the user wants to analyze another call
// ============================================================

import RiskGauge from './RiskGauge.jsx'
import { getRiskTheme } from '../data/riskTheme.js'
import './ResultsDashboard.css'

export default function ResultsDashboard({ result, onReset }) {
  const {
    transcript,
    voice_risk,
    scam_risk,
    overall_risk,
    risk_level,
    threats,
    recommended_action,
    ledger_status,
  } = result

  const theme = getRiskTheme(risk_level)

  return (
    <div className="page results-page">
      <div className="brand-row">
        <div className="brand-mark">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M12 2 L20 5.5 V11 C20 16.5 16.5 20.5 12 22 C7.5 20.5 4 16.5 4 11 V5.5 Z" fill="#0a0e1a" />
          </svg>
        </div>
        <span className="brand-name">Voxy</span>
        <span className="brand-tag">ANALYSIS COMPLETE</span>
      </div>

      {/* --- Top banner: overall verdict --- */}
      <div className="verdict-banner glass-panel" style={{ '--verdict-color': theme.color }}>
        <RiskGauge score={overall_risk} theme={theme} />
        <div className="verdict-text">
          <span className="verdict-pill" style={{ background: theme.bg, color: theme.color }}>
            {theme.label}
          </span>
          <h2 className="verdict-headline">{theme.message}</h2>
          <p className="verdict-sub">Overall risk score based on voice and conversation analysis.</p>
        </div>
      </div>

      {/* --- Sub-scores: voice vs. scam --- */}
      <div className="subscore-grid">
        <SubScoreCard label="Voice Authenticity Risk" value={voice_risk} icon={<MicIcon />} />
        <SubScoreCard label="Scam Conversation Risk" value={scam_risk} icon={<ChatIcon />} />
      </div>

      {/* --- Detected threats --- */}
      {threats?.length > 0 && (
        <section className="section-block">
          <h3 className="section-title">Detected Threats</h3>
          <div className="threat-list">
            {threats.map((threat) => (
              <span className="threat-badge" key={threat}>
                <WarnIcon />
                {threat}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* --- Recommended action --- */}
      <section className="section-block">
        <div className="action-card glass-panel" style={{ '--verdict-color': theme.color }}>
          <div className="action-icon">
            <ShieldWarnIcon />
          </div>
          <div>
            <h3 className="section-title action-title">Recommended Action</h3>
            <p className="action-text">{recommended_action}</p>
          </div>
        </div>
      </section>

      {/* --- Transcript --- */}
      <section className="section-block">
        <h3 className="section-title">Call Transcript</h3>
        <div className="transcript-panel glass-panel">
          <p className="transcript-text">“{transcript}”</p>
        </div>
      </section>

      {/* --- Ledger status --- */}
      <section className="section-block ledger-row">
        <div className="ledger-chip">
          <LedgerIcon />
          <span>Pattern record: <strong>{ledger_status}</strong></span>
        </div>
      </section>

      <button className="reset-btn" onClick={onReset}>
        Analyze Another Call
      </button>
    </div>
  )
}

function SubScoreCard({ label, value, icon }) {
  const theme = getRiskTheme(scoreToLevel(value))
  return (
    <div className="subscore-card glass-panel">
      <div className="subscore-top">
        <span className="subscore-icon" style={{ color: theme.color }}>
          {icon}
        </span>
        <span className="subscore-value" style={{ color: theme.color }}>
          {value}
        </span>
      </div>
      <p className="subscore-label">{label}</p>
      <div className="subscore-bar-track">
        <div
          className="subscore-bar-fill"
          style={{ width: `${value}%`, background: theme.color }}
        />
      </div>
    </div>
  )
}

// Converts a raw 0-100 score into a risk_level string, using the
// same bands defined in the integration contract (Risk Engine section).
function scoreToLevel(score) {
  if (score >= 80) return 'CRITICAL'
  if (score >= 60) return 'HIGH RISK'
  if (score >= 30) return 'SUSPICIOUS'
  return 'LOW'
}

/* ---------------- inline icons ---------------- */

function MicIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <rect x="9" y="2" width="6" height="12" rx="3" stroke="currentColor" strokeWidth="1.7" />
      <path d="M5 11a7 7 0 0 0 14 0M12 18v3" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  )
}

function ChatIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path
        d="M4 5h16v11H8l-4 4V5Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function WarnIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
      <path d="M12 3 22 20H2Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M12 10v4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <circle cx="12" cy="17.3" r="0.9" fill="currentColor" />
    </svg>
  )
}

function ShieldWarnIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <path
        d="M12 2 L20 5.5 V11 C20 16.5 16.5 20.5 12 22 C7.5 20.5 4 16.5 4 11 V5.5 Z"
        stroke="currentColor"
        strokeWidth="1.7"
      />
      <path d="M12 8v5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <circle cx="12" cy="15.6" r="0.9" fill="currentColor" />
    </svg>
  )
}

function LedgerIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
      <rect x="4" y="3" width="16" height="18" rx="2" stroke="currentColor" strokeWidth="1.6" />
      <path d="M8 8h8M8 12h8M8 16h5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  )
}
