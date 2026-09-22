/**
 * src/main.tsx
 * ────────────
 * Vite entry point. Mounts the React application into the #root div.
 * This is the first file executed by the browser bundle.
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
