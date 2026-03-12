/**
 * S-03 Pipeline Monitor — live view of a run in progress.
 * Shows phase progress, real-time agent logs, section status tiles,
 * and token/cost tracking.
 */
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { runsApi, sectionsApi } from '../../services/api'
import { useRunStatus } from '../../hooks/useRunStatus'
import AgentLogPanel from '../../components/agent-log/AgentLogPanel'
import ProgressBar from '../../components/ui/ProgressBar'
import StatusBadge from '../../components/ui/StatusBadge'
import TokenUsageBar from '../../components/ui/TokenUsageBar'
import { format } from 'date-fns'

const SECTION_TITLES: Record<number, string> = {
  1:  'Title Page', 2: 'Synopsis', 3: 'TOC', 4: 'Ethics',
  5:  'Investigators', 6: 'Study Dates', 7: 'Objectives', 8: 'Design',
  9:  'Study Patients', 10: 'Treatments', 11: 'Efficacy Evaluation',
  12: 'Safety Evaluation', 13: 'Discussion & Conclusions',
  14: 'TFL', 15: 'References', 16: 'Appendices',
}

export default function PipelinePage() {
  const { runId } = useParams<{ runId: string }>()
  const id = Number(runId)

  const { data: run } = useQuery({
    queryKey: ['run', id],
    queryFn: () => runsApi.get(id).then((r) => r.data),
    refetchInterval: 5000,
  })

  const { data: sections = [] } = useQuery({
    queryKey: ['sections', id],
    queryFn: () => sectionsApi.list(id).then((r) => r.data),
    refetchInterval: 5000,
  })

  const { status, progress, currentAgent, logs, connected } = useRunStatus(id, run?.run_id ?? null)

  const displayStatus = status || run?.status || 'pending'
  const displayProgress = progress || (run ? ((run.completed_sections ?? 0) / Math.max(run.total_sections ?? 16, 1)) * 100 : 0)

  const totalTokens = run?.total_tokens_used ?? 0
  const totalCost   = run?.total_cost_usd ?? 0

  const isTerminal = ['completed', 'failed', 'awaiting_review'].includes(displayStatus)

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900 flex items-center gap-3">
            {run?.run_name ?? 'Loading...'}
            <StatusBadge status={displayStatus} />
            {!connected && (
              <span className="text-xs text-yellow-600 bg-yellow-50 px-2 py-0.5 rounded-full">
                ⚡ Polling
              </span>
            )}
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Run #{id} · Started {run ? format(new Date(run.created_at), 'dd MMM yyyy, HH:mm') : '—'}
          </p>
        </div>
        {isTerminal && (
          <Link to={`/runs/${id}`} className="btn-primary text-sm">
            View Results →
          </Link>
        )}
      </div>

      {/* Progress */}
      <div className="card p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-gray-700 text-sm">Pipeline Progress</h2>
          {currentAgent && (
            <span className="text-xs text-brand-600 bg-brand-50 px-3 py-1 rounded-full">
              🤖 {currentAgent}
            </span>
          )}
        </div>
        <ProgressBar value={displayProgress} />
        <div className="flex gap-4 text-xs text-gray-500">
          <span>✅ {run?.completed_sections ?? 0} completed</span>
          <span>❌ {run?.failed_sections ?? 0} failed</span>
          <span>📋 {run?.total_sections ?? 16} total</span>
        </div>
        {(totalTokens > 0 || totalCost > 0) && (
          <TokenUsageBar tokensUsed={totalTokens} costUsd={totalCost} />
        )}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Section tiles */}
        <div className="card p-5">
          <h2 className="font-semibold text-gray-700 text-sm mb-4">Section Status</h2>
          <div className="grid grid-cols-4 gap-2">
            {Array.from({ length: 16 }, (_, i) => i + 1).map((n) => {
              const sec = sections.find((s) => s.section_number === n)
              const sectionStatus = sec?.status ?? 'pending'
              const statusColors: Record<string, string> = {
                completed:          'bg-green-100 text-green-700 border-green-200',
                retried_completed:  'bg-green-100 text-green-700 border-green-200',
                in_progress:        'bg-blue-100 text-blue-700 border-blue-200 animate-pulse',
                rerun_pending:      'bg-blue-100 text-blue-700 border-blue-200 animate-pulse',
                failed:             'bg-red-100 text-red-700 border-red-200',
                pending:            'bg-gray-100 text-gray-500 border-gray-200',
              }
              // Human-edited sections shown in purple regardless of status
              const cls = sec?.is_edited
                ? 'bg-purple-100 text-purple-700 border-purple-200'
                : (statusColors[sectionStatus] ?? statusColors.pending)
              return (
                <Link
                  key={n}
                  to={sec ? `/runs/${id}/sections/${n}` : '#'}
                  className={`border rounded-lg p-2 text-center transition-all hover:shadow-sm ${cls}`}
                >
                  <div className="font-bold text-sm">S{n}</div>
                  <div className="text-[10px] truncate mt-0.5">{SECTION_TITLES[n] ?? `Section ${n}`}</div>
                </Link>
              )
            })}
          </div>
        </div>

        {/* Live Agent Log */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-gray-700 text-sm">Live Agent Log</h2>
            <span className={`w-2 h-2 rounded-full ${connected && !isTerminal ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`} />
          </div>
          <AgentLogPanel logs={logs} height="350px" />
        </div>
      </div>

      {/* Awaiting Review Banner */}
      {displayStatus === 'awaiting_review' && (
        <div className="card p-5 bg-yellow-50 border-yellow-200">
          <div className="flex items-start gap-4">
            <span className="text-3xl">⏳</span>
            <div>
              <h3 className="font-semibold text-yellow-800">Awaiting Compliance Review</h3>
              <p className="text-sm text-yellow-700 mt-1">
                The AI pipeline has completed all sections. A Reviewer or Administrator
                must review and sign the compliance report before the final documents can be generated.
              </p>
              <Link to={`/runs/${id}/compliance`} className="btn-primary mt-3 text-sm inline-flex">
                Review Compliance Report →
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
