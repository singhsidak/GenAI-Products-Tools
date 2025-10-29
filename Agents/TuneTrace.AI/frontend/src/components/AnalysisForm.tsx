import { useState } from 'react'
import './AnalysisForm.css'

interface AnalysisFormProps {
  onAnalyze: (input: string) => void
  loading: boolean
}

const examples = [
  "Lose Yourself by Eminem",
  "Bohemian Rhapsody by Queen",
  "Blinding Lights by The Weeknd",
  "Smells Like Teen Spirit by Nirvana"
]

export default function AnalysisForm({ onAnalyze, loading }: AnalysisFormProps) {
  const [input, setInput] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !loading) {
      onAnalyze(input.trim())
    }
  }

  const handleExampleClick = (example: string) => {
    setInput(example)
  }

  return (
    <div className="analysis-form-container">
      <form onSubmit={handleSubmit} className="analysis-form">
        <div className="form-group">
          <label htmlFor="song-input" className="form-label">
            Enter Song Name, Artist, or URL
          </label>
          <textarea
            id="song-input"
            className="form-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="e.g., 'Lose Yourself by Eminem' or 'https://youtube.com/watch?v=xyz'"
            rows={3}
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          disabled={!input.trim() || loading}
        >
          {loading ? 'Analyzing...' : 'Analyze Song'}
        </button>
      </form>

      <div className="examples-section">
        <p className="examples-label">Try an example:</p>
        <div className="examples-grid">
          {examples.map((example, index) => (
            <button
              key={index}
              className="example-chip"
              onClick={() => handleExampleClick(example)}
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      <div className="info-cards">
        <div className="info-card">
          <div className="info-icon">🎯</div>
          <div className="info-content">
            <h3>20-Parameter Analysis</h3>
            <p>Comprehensive evaluation across vibe, genre, mood, tempo, and more</p>
          </div>
        </div>
        <div className="info-card">
          <div className="info-icon">🎲</div>
          <div className="info-content">
            <h3>Wildcard Recommendations</h3>
            <p>direct matches + cross-genre discovery for variety</p>
          </div>
        </div>
        <div className="info-card">
          <div className="info-icon">🌐</div>
          <div className="info-content">
            <h3>Real-time Data</h3>
            <p>Internet-enabled AI with current music information</p>
          </div>
        </div>
      </div>
    </div>
  )
}


