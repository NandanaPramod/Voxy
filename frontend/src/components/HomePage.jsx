// ============================================================
// HomePage.jsx
// The very first screen. Shows the Voxy hero + lets the user
// pick an audio file (by dragging it in, or clicking to browse).
//
// Props:
//   onAnalyze(file) — called when the user clicks "Analyze Call"
// ============================================================

import { useRef, useState } from 'react'
import './HomePage.css'

// Simple check so we don't try to "analyze" a .png someone drops by accident.
function isAudioFile(file) {
  return file && (file.type.startsWith('audio/') || /\.(mp3|wav|m4a|ogg|flac)$/i.test(file.name))
}

function formatFileSize(bytes) {
  if (!bytes) return ''
  const mb = bytes / (1024 * 1024)
  return mb >= 1 ? `${mb.toFixed(1)} MB` : `${Math.max(1, Math.round(bytes / 1024))} KB`
}

export default function HomePage({ onAnalyze }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  function handleFiles(fileList) {
    const file = fileList?.[0]
    if (!file) return
    if (!isAudioFile(file)) {
      setError('That doesn\'t look like an audio file. Try .mp3, .wav, or .m4a.')
      return
    }
    setError('')
    setSelectedFile(file)
  }

  function handleDrop(e) {
    e.preventDefault()
    setIsDragging(false)
    handleFiles(e.dataTransfer.files)
  }

  return (
    <div className="page home-page">
      <div className="brand-row">
        <div className="brand-mark">
          <ShieldIcon />
        </div>
        <span className="brand-name">Voxy</span>
        <span className="brand-tag">SCAM CALL SHIELD</span>
      </div>

      <div className="hero">
        <div className="hero-waveform" aria-hidden="true">
          <Waveform />
        </div>
        <h1 className="hero-title">
          Know if a call is <span className="hero-title-accent">safe</span> before
          you say a word.
        </h1>
        <p className="hero-subtitle">
          Drop in a call recording. Voxy checks the voice and the words for scam
          patterns — bank impersonation, OTP requests, fake urgency — in seconds.
        </p>
      </div>

      <div
        className={`dropzone glass-panel ${isDragging ? 'dropzone-active' : ''} ${
          selectedFile ? 'dropzone-filled' : ''
        }`}
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') fileInputRef.current?.click()
        }}
        aria-label="Upload a call recording"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          hidden
          onChange={(e) => handleFiles(e.target.files)}
        />

        {!selectedFile ? (
          <>
            <div className="dropzone-icon">
              <UploadIcon />
            </div>
            <p className="dropzone-title">Drag & drop a call recording</p>
            <p className="dropzone-hint">or click to browse · MP3, WAV, M4A</p>
          </>
        ) : (
          <>
            <div className="dropzone-icon dropzone-icon-selected">
              <FileIcon />
            </div>
            <p className="dropzone-title">{selectedFile.name}</p>
            <p className="dropzone-hint">{formatFileSize(selectedFile.size)} · ready to analyze</p>
          </>
        )}
      </div>

      {error && <p className="dropzone-error">{error}</p>}

      <button
        className="analyze-btn"
        disabled={!selectedFile}
        onClick={() => selectedFile && onAnalyze(selectedFile)}
      >
        Analyze Call
        <ArrowIcon />
      </button>

      <div className="trust-row">
        <TrustItem label="Voice authenticity" />
        <TrustItem label="Conversation risk" />
        <TrustItem label="Tamper-evident record" />
      </div>
    </div>
  )
}

function TrustItem({ label }) {
  return (
    <div className="trust-item">
      <span className="trust-dot" />
      {label}
    </div>
  )
}

/* ---------------- inline icons (no icon library needed) ---------------- */

function ShieldIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path
        d="M12 2 L20 5.5 V11 C20 16.5 16.5 20.5 12 22 C7.5 20.5 4 16.5 4 11 V5.5 Z"
        fill="#0a0e1a"
      />
      <path
        d="M8.5 12 L11 14.5 L16 9"
        stroke="#eef2ff"
        strokeWidth="1.8"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function UploadIcon() {
  return (
    <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
      <path
        d="M12 15V4M12 4l-4 4M12 4l4 4"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
      />
    </svg>
  )
}

function FileIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
      <path
        d="M7 3h7l5 5v11a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <path d="M14 3v5h5" stroke="currentColor" strokeWidth="1.6" />
      <path d="M9 13.5l2 2 4-4.2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function ArrowIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
      <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

// A row of little bars that idly "breathe" — evokes an audio waveform
// without needing any real audio-processing code.
function Waveform() {
  const heights = [10, 18, 28, 40, 55, 68, 55, 40, 62, 45, 30, 20, 34, 22, 14, 10]
  return (
    <div className="waveform-bars">
      {heights.map((h, i) => (
        <span
          key={i}
          className="waveform-bar"
          style={{ '--h': `${h}%`, animationDelay: `${i * 0.07}s` }}
        />
      ))}
    </div>
  )
}
