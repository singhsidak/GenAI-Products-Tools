/**
 * Generic WebSocket hook with auto-reconnect and keepalive.
 */
import { useEffect, useRef, useCallback, useState } from 'react'

export type WSMessage = Record<string, unknown>

interface UseWebSocketOptions {
  onMessage: (msg: WSMessage) => void
  enabled?: boolean
}

export function useWebSocket(url: string | null, options: UseWebSocketOptions) {
  const { onMessage, enabled = true } = options
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>()
  const [connected, setConnected] = useState(false)

  const connect = useCallback(() => {
    if (!url || !enabled) return
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(`${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}${url}`)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as WSMessage
        // Ignore keepalive pings
        if (data.type === 'ping') return
        onMessage(data)
      } catch {
        // Ignore malformed messages
      }
    }

    ws.onclose = () => {
      setConnected(false)
      // Reconnect after 3 seconds
      reconnectTimer.current = setTimeout(connect, 3000)
    }

    ws.onerror = () => {
      ws.close()
    }
  }, [url, enabled, onMessage])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [connect])

  return { connected }
}
