import { useEffect, useState } from 'react'
import './DownloadProgress.css'

interface Song {
  title: string
  artist: string
  status: 'pending' | 'downloading' | 'completed' | 'failed'
  progress?: number
}

export default function DownloadProgress() {
  const [connected, setConnected] = useState(false)
  const [playlistName, setPlaylistName] = useState('')
  const [songs, setSongs] = useState<Song[]>([])
  const [currentSong, setCurrentSong] = useState<string>('')
  const [overallStatus, setOverallStatus] = useState<'starting' | 'downloading' | 'completed' | 'error'>('starting')
  const [stats, setStats] = useState({ completed: 0, failed: 0, total: 0 })
  const [error, setError] = useState<string>('')

  useEffect(() => {
    // Get download ID from URL
    const params = new URLSearchParams(window.location.search)
    const downloadId = params.get('id')
    const playlistNameParam = params.get('name')

    if (!downloadId) {
      setError('No download ID provided')
      setOverallStatus('error')
      return
    }

    if (playlistNameParam) {
      setPlaylistName(decodeURIComponent(playlistNameParam))
    }

    // Connect to SSE endpoint
    const eventSource = new EventSource(
      `http://localhost:8000/download-progress/${downloadId}`
    )

    eventSource.onopen = () => {
      setConnected(true)
    }

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        console.log('SSE Message:', data)

        if (data.type === 'error') {
          setError(data.message)
          setOverallStatus('error')
          eventSource.close()
          return
        }

        if (data.type === 'connected') {
          console.log('Connected to progress stream')
          return
        }

        // Handle download status updates
        if (data.status) {
          setOverallStatus(data.status)
          
          if (data.current_song) {
            setCurrentSong(data.current_song)
          }

          // Update stats
          if (data.completed && data.failed && data.total) {
            setStats({
              completed: data.completed.length,
              failed: data.failed.length,
              total: data.total
            })
          }

          // Build songs list
          const allSongs: Song[] = []
          
          // Completed songs
          data.completed?.forEach((songTitle: string) => {
            allSongs.push({
              title: songTitle.split(' - ')[1] || songTitle,
              artist: songTitle.split(' - ')[0] || '',
              status: 'completed',
              progress: 100
            })
          })

          // Failed songs
          data.failed?.forEach((songTitle: string) => {
            allSongs.push({
              title: songTitle.split(' - ')[1] || songTitle,
              artist: songTitle.split(' - ')[0] || '',
              status: 'failed',
              progress: 0
            })
          })

          // Current song
          if (data.current_song && data.status === 'downloading') {
            allSongs.push({
              title: data.current_song.split(' - ')[1] || data.current_song,
              artist: data.current_song.split(' - ')[0] || '',
              status: 'downloading',
              progress: 50
            })
          }

          setSongs(allSongs)
        }

        // Handle completion
        if (data.type === 'complete' || data.status === 'completed') {
          setOverallStatus('completed')
          eventSource.close()
        }

      } catch (err) {
        console.error('Error parsing SSE data:', err)
      }
    }

    eventSource.onerror = (err) => {
      console.error('SSE Error:', err)
      setConnected(false)
      setError('Connection lost')
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅'
      case 'downloading': return '⏳'
      case 'failed': return '❌'
      default: return '⏸️'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'status-completed'
      case 'downloading': return 'status-downloading'
      case 'failed': return 'status-failed'
      default: return 'status-pending'
    }
  }

  return (
    <div className="download-progress-page">
      <div className="progress-header">
        <h1>📥 Downloading Playlist</h1>
        {playlistName && <h2>"{playlistName}"</h2>}
        
        <div className="connection-status">
          {connected ? (
            <span className="status-connected">🟢 Connected</span>
          ) : (
            <span className="status-disconnected">🔴 Disconnected</span>
          )}
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <h3>❌ Error</h3>
          <p>{error}</p>
        </div>
      )}

      <div className="progress-stats">
        <div className="stat-card">
          <div className="stat-value">{stats.completed}</div>
          <div className="stat-label">Completed</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.total - stats.completed - stats.failed}</div>
          <div className="stat-label">Remaining</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.failed}</div>
          <div className="stat-label">Failed</div>
        </div>
        <div className="stat-card stat-total">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total</div>
        </div>
      </div>

      {currentSong && overallStatus === 'downloading' && (
        <div className="current-download">
          <div className="current-label">Currently Downloading:</div>
          <div className="current-song">{currentSong}</div>
          <div className="progress-bar-container">
            <div className="progress-bar-fill"></div>
          </div>
        </div>
      )}

      <div className="songs-list">
        <h3>Songs</h3>
        {songs.length === 0 && overallStatus !== 'error' && (
          <div className="loading-message">
            <div className="spinner"></div>
            <p>Preparing download...</p>
          </div>
        )}
        
        {songs.map((song, index) => (
          <div key={index} className={`song-item ${getStatusColor(song.status)}`}>
            <div className="song-icon">{getStatusIcon(song.status)}</div>
            <div className="song-info">
              <div className="song-title">{song.title}</div>
              <div className="song-artist">{song.artist}</div>
            </div>
            {song.progress !== undefined && (
              <div className="song-progress">
                {song.status === 'downloading' && (
                  <div className="mini-progress-bar">
                    <div className="mini-progress-fill" style={{ width: `${song.progress}%` }}></div>
                  </div>
                )}
                {song.status === 'completed' && <span className="progress-text">Done!</span>}
                {song.status === 'failed' && <span className="progress-text error-text">Failed</span>}
              </div>
            )}
          </div>
        ))}
      </div>

      {overallStatus === 'completed' && (
        <div className="completion-banner">
          <h2>🎉 Download Complete!</h2>
          <p>All songs have been downloaded to your playlist folder</p>
          <button onClick={() => window.close()} className="close-button">
            Close Window
          </button>
        </div>
      )}
    </div>
  )
}


