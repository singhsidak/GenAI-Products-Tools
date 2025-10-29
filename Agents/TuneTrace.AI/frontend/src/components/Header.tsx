import './Header.css'

export default function Header() {
  return (
    <header className="header">
      <div className="header-container">
        <div className="header-left">
          <span className="logo">🎵</span>
          <span className="logo-text">TuneTrace.AI</span>
        </div>
        <div className="header-right">
          <span className="badge">v2.0</span>
          <span className="badge badge-ai">AI Powered</span>
        </div>
      </div>
    </header>
  )
}



