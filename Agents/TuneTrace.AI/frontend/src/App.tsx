import { useState } from 'react'
import './App.css'
import AnalysisForm from './components/AnalysisForm'
import ResultsDisplay from './components/ResultsDisplay'
import Header from './components/Header'
import { analyzeSong, getMoreRecommendations } from './lib/api'

interface AnalysisResult {
  success: boolean
  data?: any
  error?: string
  input?: string
}

function App() {
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)

  const handleAnalyze = async (songInput: string) => {
    setLoading(true)
    setResult(null)

    try {
      const response = await analyzeSong(songInput)
      setResult(response)
    } catch (error: any) {
      setResult({
        success: false,
        error: error.message || 'Failed to analyze song',
        input: songInput
      })
    } finally {
      setLoading(false)
    }
  }

  const handleMoreRecommendations = async () => {
    if (!result || !result.input) return

    setLoadingMore(true)

    try {
      const response = await getMoreRecommendations(result.input)
      if (response.success && response.data) {
        // Append new recommendations to existing ones
        setResult(prev => {
          if (!prev || !prev.data) return response
          
          return {
            ...prev,
            data: {
              ...prev.data,
              recommendations: [
                ...(prev.data.recommendations || []),
                ...(response.data.recommendations || [])
              ]
            }
          }
        })
      }
    } catch (error: any) {
      console.error('Failed to get more recommendations:', error)
    } finally {
      setLoadingMore(false)
    }
  }

  return (
    <div className="app">
      <Header />
      
      <main className="main-content">
        <div className="container">
          <section className="hero">
            <h1 className="hero-title">
              <span className="gradient-text">TuneTrace.AI</span>
            </h1>
            <p className="hero-subtitle">
              Advanced Music Analysis & Intelligent Recommendations
            </p>
            <p className="hero-description">
              Powered by AI • 20-Parameter Rubric • Real-time Internet Access
            </p>
          </section>

          <AnalysisForm onAnalyze={handleAnalyze} loading={loading} />

          {loading && (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Analyzing music with AI...</p>
              <p className="loading-subtext">This may take 10-15 seconds</p>
            </div>
          )}

          {result && !loading && (
            <ResultsDisplay 
              result={result} 
              onMoreRecommendations={handleMoreRecommendations}
              loadingMore={loadingMore}
            />
          )}
        </div>
      </main>

      <footer className="footer">
        <p>TuneTrace.AI v2.0 • Powered by Google Gemini 2.0</p>
      </footer>
    </div>
  )
}

export default App


