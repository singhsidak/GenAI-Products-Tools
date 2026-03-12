/**
 * S-06 Section Editor — view, edit, and rerun individual CSR sections.
 * Shows content, compliance trace, token usage per section.
 * Reviewer role: read-only. User/Admin: editable.
 */
import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { sectionsApi, type ComplianceTraceItem } from '../../services/api'
import { useAuthStore } from '../../store/authStore'
import StatusBadge from '../../components/ui/StatusBadge'
import TokenUsageBar from '../../components/ui/TokenUsageBar'
import toast from 'react-hot-toast'

const SECTION_NAMES: Record<number, string> = {
  1:'Title Page',2:'Synopsis',3:'Table of Contents',4:'Ethics',
  5:'Investigators',6:'Study Dates',7:'Objectives',8:'Study Design',
  9:'Study Patients',10:'Treatments',11:'Efficacy Evaluation',
  12:'Safety Evaluation',13:'Discussion & Conclusions',
  14:'Tables, Figures, Listings',15:'References',16:'Appendices',
}

function ComplianceTracePanel({ trace }: { trace: ComplianceTraceItem[] }) {
  if (!trace.length) return null
  return (
    <div className="card p-4">
      <h3 className="font-semibold text-sm text-gray-700 mb-3">Compliance Trace</h3>
      <div className="space-y-2">
        {trace.map((item, i) => (
          <div key={i} className="flex items-start gap-3 text-xs">
            <StatusBadge status={item.status} />
            <div className="flex-1">
              <span className="font-mono text-gray-500 mr-2">{item.rule_id}</span>
              <span className="text-gray-700">{item.rule_description}</span>
              {item.details && <p className="text-gray-400 mt-0.5">{item.details}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function SectionEditorPage() {
  const { runId, sectionNumber } = useParams<{ runId: string; sectionNumber: string }>()
  const rid = Number(runId)
  const sn  = Number(sectionNumber)
  const qc  = useQueryClient()
  const { user } = useAuthStore()

  const canEdit = user?.role !== 'reviewer'

  const { data: section, isLoading } = useQuery({
    queryKey: ['section', rid, sn],
    queryFn: () => sectionsApi.get(rid, sn).then((r) => r.data),
  })

  const [content, setContent]       = useState('')
  const [editReason, setEditReason] = useState('')
  const [isDirty, setIsDirty]       = useState(false)
  const [showPreview, setShowPreview] = useState(false)

  useEffect(() => {
    if (section) {
      setContent(section.content ?? '')
      setIsDirty(false)
    }
  }, [section])

  const saveMutation = useMutation({
    mutationFn: () => sectionsApi.update(rid, sn, { content }),
    onSuccess: (res) => {
      toast.success('Section saved')
      qc.setQueryData(['section', rid, sn], res.data)
      setIsDirty(false)
      setEditReason('')
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail ?? 'Save failed'),
  })

  const rerunMutation = useMutation({
    mutationFn: () => sectionsApi.rerun(rid, sn),
    onSuccess: () => {
      toast.success('Section queued for regeneration')
      qc.invalidateQueries({ queryKey: ['section', rid, sn] })
    },
    onError: () => toast.error('Rerun failed'),
  })

  if (isLoading) return <div className="p-6 text-gray-500">Loading section...</div>
  if (!section)  return <div className="p-6 text-red-500">Section not found</div>

  return (
    <div className="p-6 space-y-5 max-w-5xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Link to={`/runs/${rid}`} className="hover:text-brand-600">Run #{rid}</Link>
        <span>›</span>
        <span className="text-gray-800 font-medium">Section {sn}: {SECTION_NAMES[sn]}</span>
      </div>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            {sn}. {SECTION_NAMES[sn]}
          </h1>
          <div className="flex items-center gap-3 mt-2 flex-wrap">
            <StatusBadge status={section.status} />
            {section.is_edited && <span className="badge-purple">✏️ Edited</span>}
            {section.word_count && (
              <span className="text-xs text-gray-500">{section.word_count.toLocaleString()} words</span>
            )}
            {section.agent_name && (
              <span className="text-xs text-gray-500">🤖 {section.agent_name}</span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowPreview((p) => !p)}
            className="btn-ghost text-sm"
          >
            {showPreview ? '✏️ Edit' : '👁 Preview'}
          </button>
          <button
            onClick={() => rerunMutation.mutate()}
            className="btn-secondary text-sm"
            disabled={rerunMutation.isPending}
          >
            🔄 Regenerate
          </button>
        </div>
      </div>

      {/* Token usage */}
      {(section.tokens_used || section.generation_cost_usd) && (
        <TokenUsageBar
          tokensUsed={section.tokens_used ?? 0}
          costUsd={section.generation_cost_usd ?? 0}
        />
      )}

      {/* Editor / Preview */}
      <div className="card overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between bg-gray-50">
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            {showPreview ? 'Preview' : 'Content Editor'}
          </span>
          {!canEdit && (
            <span className="text-xs text-yellow-600 bg-yellow-50 px-2 py-0.5 rounded-full">
              Read-only (Reviewer)
            </span>
          )}
        </div>

        {showPreview ? (
          <div
            className="prose prose-sm max-w-none p-6 font-serif whitespace-pre-wrap text-gray-800"
            style={{ fontFamily: 'Georgia, serif', lineHeight: '1.8' }}
          >
            {content}
          </div>
        ) : (
          <textarea
            value={content}
            onChange={(e) => { setContent(e.target.value); setIsDirty(true) }}
            readOnly={!canEdit}
            className="w-full p-5 font-mono text-sm text-gray-800 bg-white resize-none focus:outline-none"
            style={{ minHeight: '500px', lineHeight: '1.7' }}
            placeholder="Section content will appear here..."
          />
        )}
      </div>

      {/* Save bar */}
      {canEdit && isDirty && (
        <div className="card p-4 bg-blue-50 border-blue-200">
          <div className="flex items-end gap-3">
            <div className="flex-1">
              <label className="label text-xs text-blue-700">Edit Reason (optional)</label>
              <input
                type="text"
                className="input text-sm"
                placeholder="Describe what you changed and why..."
                value={editReason}
                onChange={(e) => setEditReason(e.target.value)}
                maxLength={500}
              />
            </div>
            <button
              onClick={() => saveMutation.mutate()}
              className="btn-primary"
              disabled={saveMutation.isPending}
            >
              {saveMutation.isPending ? 'Saving...' : '💾 Save Changes'}
            </button>
            <button
              onClick={() => { setContent(section.content ?? ''); setIsDirty(false) }}
              className="btn-ghost"
            >
              Discard
            </button>
          </div>
        </div>
      )}

      {/* Compliance trace */}
      {(section.compliance_trace?.length ?? 0) > 0 && (
        <ComplianceTracePanel trace={section.compliance_trace!} />
      )}

      {/* Edit history note */}
      {(section.edit_count ?? 0) > 0 && (
        <p className="text-xs text-gray-400">
          This section has been manually edited {section.edit_count ?? 0} time{(section.edit_count ?? 0) !== 1 ? 's' : ''}.
        </p>
      )}
    </div>
  )
}
