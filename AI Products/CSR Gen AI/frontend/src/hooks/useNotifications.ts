/**
 * Hook: subscribes to real-time user notifications via WebSocket.
 */
import { useState, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useWebSocket, type WSMessage } from './useWebSocket'
import { useAuthStore } from '../store/authStore'
import type { Notification } from '../services/api'

export function useNotifications() {
  const user = useAuthStore((s) => s.user)
  const queryClient = useQueryClient()
  const [unreadCount, setUnreadCount] = useState(0)
  const [latest, setLatest] = useState<Notification | null>(null)

  const handleMessage = useCallback((msg: WSMessage) => {
    if (msg.type === 'notification') {
      // push_to_user sends the notification fields directly (no 'data' wrapper)
      const notif: Notification = {
        id: msg.id as number,
        run_id: msg.run_id as string | null,
        event_type: msg.event_type as string,
        message: msg.message as string,
        is_read: false,
        created_at: msg.timestamp as string,
      }
      setLatest(notif)
      setUnreadCount((c) => c + 1)
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    }
  }, [queryClient])

  const wsUrl = user ? `/ws/user/${user.id}` : null
  const { connected } = useWebSocket(wsUrl, {
    onMessage: handleMessage,
    enabled: !!user,
  })

  return { unreadCount, setUnreadCount, latest, connected }
}
