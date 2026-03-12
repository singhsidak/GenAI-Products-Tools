/**
 * Hook: subscribes to real-time run status updates via WebSocket.
 * Falls back to polling every 10 seconds if WS is disconnected.
 */
import { useState, useCallback, useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useWebSocket, type WSMessage } from './useWebSocket'
import type { AgentLog } from '../services/api'

interface RunStatusState {
  status: string
  progress: number          // 0-100
  currentAgent: string | null
  logs: AgentLog[]
}

/**
 * @param runId      Numeric DB id — used for query-cache invalidation
 * @param wsRunId    String run_id (e.g. "AB3C") — used for the WS URL.
 *                   Only connect once the caller has the string run_id.
 */
export function useRunStatus(runId: number | null, wsRunId?: string | null) {
  const queryClient = useQueryClient()
  const [state, setState] = useState<RunStatusState>({
    status: '',
    progress: 0,
    currentAgent: null,
    logs: [],
  })

  const handleMessage = useCallback((msg: WSMessage) => {
    // Backend WSEvent uses 'event_type', not 'type' (type='ping' is handled in useWebSocket)
    const eventType = (msg.event_type ?? msg.type) as string
    const payload = (msg.payload ?? {}) as Record<string, unknown>

    if (eventType === 'progress') {
      setState((prev) => ({
        ...prev,
        progress: (payload.percent as number) ?? prev.progress,
        currentAgent: (payload.phase_label as string) ?? prev.currentAgent,
      }))
      if (runId) {
        queryClient.invalidateQueries({ queryKey: ['run', runId] })
      }
    }

    if (eventType === 'agent_log') {
      const entry: AgentLog = {
        id: 0,
        agent_name: payload.agent_name as string,
        phase: (payload.phase as string | null) ?? null,
        status: payload.status as string,
        message: (payload.message as string | null) ?? null,
        timestamp: (msg.timestamp as string) ?? new Date().toISOString(),
        input_tokens: payload.input_tokens as number | undefined,
        output_tokens: payload.output_tokens as number | undefined,
        estimated_cost_usd: payload.estimated_cost_usd as number | undefined,
      }
      setState((prev) => ({
        ...prev,
        currentAgent: entry.agent_name,
        logs: [...prev.logs, entry],
      }))
    }

    if (eventType === 'section_complete') {
      if (runId) {
        queryClient.invalidateQueries({ queryKey: ['sections', runId] })
        queryClient.invalidateQueries({ queryKey: ['run', runId] })
      }
    }

    if (eventType === 'pipeline_completed' || eventType === 'pipeline_failed') {
      setState((prev) => ({
        ...prev,
        status: eventType === 'pipeline_completed' ? 'completed' : 'failed',
        progress: eventType === 'pipeline_completed' ? 100 : prev.progress,
        currentAgent: null,
      }))
      if (runId) {
        queryClient.invalidateQueries({ queryKey: ['run', runId] })
        queryClient.invalidateQueries({ queryKey: ['runs'] })
      }
    }

    if (eventType === 'compliance_review_required') {
      if (runId) {
        queryClient.invalidateQueries({ queryKey: ['run', runId] })
      }
    }
  }, [runId, queryClient])

  // Use the string run_id for the WS URL (pipeline events are keyed by it)
  const wsUrl = wsRunId ? `/ws/run/${wsRunId}` : null
  const { connected } = useWebSocket(wsUrl, {
    onMessage: handleMessage,
    enabled: !!wsRunId,
  })

  // Polling fallback when WS is disconnected
  useEffect(() => {
    if (connected || !runId) return
    const interval = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: ['run', runId] })
    }, 10_000)
    return () => clearInterval(interval)
  }, [connected, runId, queryClient])

  return { ...state, connected }
}
