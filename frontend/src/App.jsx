// ============================================================
// App.jsx — the "traffic controller" of the whole app.
//
// Voxy has exactly 3 screens:
//   1. "home"      -> HomePage      (upload an audio file)
//   2. "analyzing" -> AnalyzingScreen (fake loading animation)
//   3. "results"   -> ResultsDashboard (the risk report)
//
// We keep track of which screen is showing using React "state"
// (the `screen` variable below). Nothing fancy like React Router —
// for 3 screens, a single variable is simpler and easier to debug.
// ============================================================

import { useState } from 'react'
import HomePage from './components/HomePage.jsx'
import AnalyzingScreen from './components/AnalyzingScreen.jsx'
import ResultsDashboard from './components/ResultsDashboard.jsx'
import { MOCK_RESULT } from './data/mockResult.js'
import './App.css'

function App() {
  // Which screen is currently visible.
  const [screen, setScreen] = useState('home')

  // The audio file the user picked (just its name/info for now).
  const [audioFile, setAudioFile] = useState(null)

  // The analysis result. Starts empty, gets filled in once
  // "analysis" finishes (right now that's mock data + a timer,
  // later this becomes the real response from POST /analyze).
  const [result, setResult] = useState(null)

  // Called by HomePage when the user clicks "Analyze Call".
  function handleAnalyze(file) {
    setAudioFile(file)
    setScreen('analyzing')

    // --------------------------------------------------------
    // BACKEND HAND-OFF POINT
    // --------------------------------------------------------
    // Right now we fake a network call with setTimeout and mock data.
    // When the backend's POST /analyze endpoint is ready, replace the
    // block below with something like:
    //
    //   const formData = new FormData()
    //   formData.append('audio', file)
    //   fetch('http://localhost:8000/analyze', { method: 'POST', body: formData })
    //     .then((res) => res.json())
    //     .then((data) => {
    //       setResult(data)
    //       setScreen('results')
    //     })
    //     .catch((err) => {
    //       console.error('Analyze request failed:', err)
    //       // TODO: show an error screen instead of results
    //     })
    //
    // The mock data below matches the EXACT JSON shape the backend
    // team promised in the integration contract, so swapping this
    // out later should not require changing ResultsDashboard at all.
    // --------------------------------------------------------
    setTimeout(() => {
      setResult(MOCK_RESULT)
      setScreen('results')
    }, 3200)
  }

  // Called by ResultsDashboard's "Analyze Another Call" button.
  function handleReset() {
    setAudioFile(null)
    setResult(null)
    setScreen('home')
  }

  return (
    <div className="app-shell">
      <div className="ambient-glow" aria-hidden="true" />

      {screen === 'home' && <HomePage onAnalyze={handleAnalyze} />}

      {screen === 'analyzing' && <AnalyzingScreen fileName={audioFile?.name} />}

      {screen === 'results' && result && (
        <ResultsDashboard result={result} onReset={handleReset} />
      )}
    </div>
  )
}

export default App
