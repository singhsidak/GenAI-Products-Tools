/**
 * Live agent log terminal panel.
 * Renders coloured log entries and auto-scrolls to bottom.
 */
import { useEffect, useRef } from 'react'
import type { AgentLog } from '../../services/api'
import { format } from 'date-fns'

interface Props {
  logs: AgentLog[]
  height?: string
}

const STATUS_CLASS: Record<string, string> = {
  started:   'log-info',
  completed: 'log-agent',
  failed:    'log-error',
  warning:   'log-warning',
}

const AGENT_ICONS: Record<string, string> = {
  guideline_enforcer:  '📏',
  indexing_agent:      '🗂️',
  tfl_agent:           '📊',
  synopsis_agent:      '📝',
  abbreviations_agent: '🔤',
  references_agent:    '📚',
  toc_agent:           '📑',
  merging_agent:       '🔧',
  compliance_validator:'✅',
}

function agentIcon(agentName: string): string {
  for (const [key, icon] of Object.entries(AGENT_ICONS)) {
    if (agentName.includes(key)) return icon
  }
  return '🤖'
}

export default function AgentLogPanel({ logs, height = '400px' }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  return (
    <div className="agent-log" style={{ height, minHeight: '200px' }}>
      {logs.length === 0 ? (
        <span className="text-gray-600 text-xs">Waiting for agent activity...</span>
      ) : (
        logs.map((log, idx) => {
          const levelClass = STATUS_CLASS[log.status?.toLowerCase() ?? ''] ?? 'log-info'
          const time = format(new Date(log.timestamp), 'HH:mm:ss')
          const icon = agentIcon(log.agent_name)
          const totalTokens = (log.input_tokens ?? 0) + (log.output_tokens ?? 0)
          const tokenInfo = totalTokens > 0
            ? ` [${totalTokens.toLocaleString()} tokens${log.estimated_cost_usd ? ` · $${log.estimated_cost_usd.toFixed(4)}` : ''}]`
            : ''

          return (
            <div key={idx} className={`${levelClass} leading-relaxed`}>
              <span className="opacity-50 mr-2">{time}</span>
              <span className="mr-2">{icon}</span>
              <span className="opacity-70 mr-2">[{log.agent_name}]</span>
              {log.phase && (
                <span className="opacity-60 mr-2">[{log.phase}]</span>
              )}
              <span>{log.message}</span>
              {tokenInfo && <span className="opacity-50 text-[10px]">{tokenInfo}</span>}
            </div>
          )
        })
      )}
      <div ref={bottomRef} />
    </div>
  )
}
