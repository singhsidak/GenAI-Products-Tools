import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import DownloadProgress from './components/DownloadProgress.tsx'
import './index.css'

// Simple routing based on URL path
const path = window.location.pathname

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {path === '/download-progress' ? <DownloadProgress /> : <App />}
  </React.StrictMode>,
)


