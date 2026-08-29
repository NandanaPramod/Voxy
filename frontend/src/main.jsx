// This is the very first file that runs in our React app.
// It finds the <div id="root"> in index.html and tells React
// to render our <App /> component inside it.

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
