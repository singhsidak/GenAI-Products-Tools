/**
 * S-05 Run Detail — section list, download buttons, retry/rerun controls.
 */
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { runsApi, sectionsApi } from '../../services/api'
import StatusBadge from '../../components/ui/StatusBadge'
import TokenUsageBar from '../../components/ui/TokenUsageBar'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

const SECTION_NAMES: Record<number, string> = {
  1:  'Title Page',           2: 'Synopsis',
  3:  'Table of Contents',    4: 'Ethics',
  5:  'Investigators',        6: 'Study Dates',
  7:  'Objectives',           8: 'Study Design',
  9:  'Study Patients',       10: 'Treatments',
  11: 'Efficacy Evaluation',  12: 'Safety Evaluation',
  13: 'Discussion & Conclusions', 14: 'Tables, Figures, Listings',
  15: 'References',           16: 'Appendices',
}

export default function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>()
  const id = Number(runId)
  const qc = useQueryClient()

  const { data: run, isLoading } = useQuery({
    queryKey: ['run', id],
    queryFn: () => runsApi.get(id).then((r) => r.data),
  })

  const { data: sections = [] } = useQuery({
    queryKey: ['sections', id],
    queryFn: () => sectionsApi.list(id).then((r) => r.data),
  })

  const retryMutation = useMutation({
    mutationFn: (sectionNumber: number) => runsApi.retrySection(id, sectionNumber),
    onSuccess: (_, sn) => {
      toast.success(`Section ${sn} queued for retry`)
      qc.invalidateQueries({ queryKey: ['sections', id] })
    },
    onError: () => toast.error('Retry failed'),
  })

  const rerunMutation = useMutation({
    mutationFn: () => runsApi.rerun(id, {}),
    onSuccess: () => {
      toast.success('Full rerun started')
      qc.invalidateQueries({ queryKey: ['run', id] })
    },
    onError: () => toast.error('Rerun failed'),
  })

  const handleDownload = async (fileType: 'pdf' | 'docx') => {
    try {
      const res = await runsApi.download(id, fileType)
      const url = URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `CSR_Run${id}.${fileType}`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      toast.error(`Failed to download ${fileType.toUpperCase()}`)
    }
  }

  if (isLoading) {
    return <div className="p-6 text-gray-500">Loading...</div>
  }

  const isCompleted  = run?.status === 'completed'
  const failedCount  = sections.filter((s) => s.status === 'failed').length
  const totalTokens  = run?.total_tokens_used ?? 0
  const totalCost    = run?.total_cost_usd ?? 0

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900 flex items-center gap-3">
            {run?.run_name}
            <StatusBadge status={run?.status ?? ''} />
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Run #{id} · Created {run ? format(new Date(run.created_at), 'dd MMM yyyy, HH:mm') : '—'}
          </p>
        </div>

        <div className="flex gap-2">
          {run?.status === 'awaiting_review' && (
            <Link to={`/runs/${id}/compliance`} className="btn-primary text-sm">
              Review Compliance
            </Link>
          )}
          {isCompleted && (
            <>
              <button onClick={() => handleDownload('pdf')}  className="btn-secondary text-sm">⬇ PDF</button>
              <button onClick={() => handleDownload('docx')} className="btn-secondary text-sm">⬇ DOCX</button>
            </>
          )}
          {failedCount > 0 && (
            <button
              onClick={() => rerunMutation.mutate()}
              className="btn-secondary text-sm"
              disabled={rerunMutation.isPending}
            >
              🔄 Rerun Failed
            </button>
          )}
        </div>
      </div>

      {/* Token usage */}
      {totalTokens > 0 && <TokenUsageBar tokensUsed={totalTokens} costUsd={totalCost} />}

      {/* Sections table */}
      <div className="card overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-700 text-sm">Sections ({sections.length})</h2>
        </div>
        <div className="divide-y divide-gray-50">
          {Array.from({ length: 16 }, (_, i) => i + 1).map((n) => {
            const sec = sections.find((s) => s.section_number === n)
            const status = sec?.status ?? 'pending'
            const isError = status === 'failed'

            return (
              <div key={n} className="flex items-center px-5 py-3 hover:bg-gray-50 transition-colors">
                <div className="w-8 text-sm font-bold text-gray-400">S{n}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800">{SECTION_NAMES[n]}</p>
                  {sec?.word_count && (
                    <p className="text-xs text-gray-400 mt-0.5">{sec.word_count.toLocaleString()} words</p>
                  )}
                </div>
                <div className="flex items-center gap-3 ml-4">
                  {sec?.is_edited && (
                    <span className="text-xs text-purple-600 bg-purple-50 px-2 py-0.5 rounded-full">✏️ Edited</span>
                  )}
                  <StatusBadge status={status} />
                  {sec && (
                    <Link
                      to={`/runs/${id}/sections/${n}`}
                      className="text-xs text-brand-600 hover:underline"
                    >
                      View
                    </Link>
                  )}
                  {isError && (
                    <button
                      onClick={() => retryMutation.mutate(n)}
                      className="text-xs text-red-600 hover:underline"
                      disabled={retryMutation.isPending}
                    >
                      Retry
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Agent logs link */}
      <div className="flex justify-end">
        <Link to={`/runs/${id}/pipeline`} className="btn-ghost text-sm">
          View Agent Logs →
        </Link>
      </div>
    </div>
  )
}
