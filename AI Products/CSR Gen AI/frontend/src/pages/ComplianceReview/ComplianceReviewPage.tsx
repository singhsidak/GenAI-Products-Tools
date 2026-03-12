/**
 * S-07 Compliance Review — view compliance report, sign to trigger merging.
 * Reviewer and Admin only.
 */
import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { complianceApi, type ComplianceAuditEntry } from '../../services/api'
import { useAuthStore } from '../../store/authStore'
import StatusBadge from '../../components/ui/StatusBadge'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export default function ComplianceReviewPage() {
  const { runId } = useParams<{ runId: string }>()
  const id = Number(runId)
  const qc = useQueryClient()
  const navigate = useNavigate()
  const { user } = useAuthStore()

  const canSign = user?.role === 'reviewer' || user?.role === 'admin'

  const { data: report, isLoading } = useQuery({
    queryKey: ['compliance', id],
    queryFn: () => complianceApi.get(id).then((r) => r.data),
  })

  const { data: audit = [] } = useQuery({
    queryKey: ['compliance-audit', id],
    queryFn: () => complianceApi.getAudit(id).then((r) => r.data),
    enabled: canSign,
  })

  const [showConfirm, setShowConfirm] = useState(false)

  const signMutation = useMutation({
    mutationFn: () => complianceApi.sign(id, { acknowledged: true }),
    onSuccess: () => {
      toast.success('Compliance report signed — merging started!')
      qc.invalidateQueries({ queryKey: ['compliance', id] })
      qc.invalidateQueries({ queryKey: ['run', id] })
      navigate(`/runs/${id}/pipeline`)
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail ?? 'Signing failed'),
  })

  if (isLoading) return <div className="p-6 text-gray-500">Loading compliance report...</div>
  if (!report)   return <div className="p-6 text-red-500">Compliance report not found</div>

  const hasDeviations = report.gcp_deviation_count > 0

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Link to={`/runs/${id}`} className="hover:text-brand-600">Run #{id}</Link>
        <span>›</span>
        <span className="text-gray-800 font-medium">Compliance Review</span>
      </div>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Compliance Report</h1>
          <p className="text-sm text-gray-500 mt-1">
            v{report.version_id} · Generated {format(new Date(report.created_at), 'dd MMM yyyy, HH:mm')}
          </p>
        </div>
        <StatusBadge status={report.overall_status} />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4">
        {[
          { label: 'GCP Deviations',       value: report.gcp_deviation_count,       color: report.gcp_deviation_count > 0       ? 'text-red-600'    : 'text-green-600' },
          { label: 'Data Not Available',   value: report.data_not_available_count,   color: report.data_not_available_count > 0 ? 'text-yellow-600' : 'text-green-600' },
        ].map(({ label, value, color }) => (
          <div key={label} className="card p-4 text-center">
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
            <p className="text-xs text-gray-500 mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Signed status */}
      {report.is_signed ? (
        <div className="card p-5 bg-green-50 border-green-200">
          <div className="flex items-center gap-3">
            <span className="text-2xl">✅</span>
            <div>
              <p className="font-semibold text-green-800">Compliance Report Signed</p>
              <p className="text-sm text-green-700 mt-0.5">
                Signed by {report.signed_by_username ?? 'unknown'} on{' '}
                {report.signed_at ? format(new Date(report.signed_at), 'dd MMM yyyy, HH:mm') : '—'}
              </p>
            </div>
          </div>
        </div>
      ) : canSign ? (
        /* Signature panel */
        <div className="card p-5 bg-yellow-50 border-yellow-200">
          <h3 className="font-semibold text-yellow-800 mb-3">Digital Signature</h3>
          <p className="text-sm text-yellow-700 mb-4">
            By signing this compliance report, you certify that you have reviewed the
            ICH E3-compliant content and approve it for document generation.
            This action is irreversible and will be recorded in the audit trail.
          </p>

          {!showConfirm ? (
            <button
              onClick={() => setShowConfirm(true)}
              className="btn-primary"
            >
              ✍️ Sign &amp; Approve
            </button>
          ) : (
            <div className="space-y-3">
              <div className="flex gap-3">
                <button
                  onClick={() => signMutation.mutate()}
                  className="btn-primary"
                  disabled={signMutation.isPending}
                >
                  {signMutation.isPending ? 'Signing...' : '✅ Confirm Signature'}
                </button>
                <button onClick={() => setShowConfirm(false)} className="btn-ghost">
                  Cancel
                </button>
              </div>
            </div>
          )}

          {hasDeviations && (
            <p className="text-xs text-red-600 mt-3">
              ⚠️ {report.gcp_deviation_count} GCP deviation{report.gcp_deviation_count !== 1 ? 's' : ''} detected.
              Review section content before signing.
            </p>
          )}
        </div>
      ) : null}

      {/* Audit trail */}
      {canSign && audit.length > 0 && (
        <div className="card p-5">
          <h3 className="font-semibold text-gray-700 text-sm mb-3">Audit Trail</h3>
          <div className="space-y-2">
            {audit.map((entry: ComplianceAuditEntry) => (
              <div key={entry.id} className="flex items-start gap-3 text-xs border-b border-gray-50 pb-2">
                <span className="text-gray-400 flex-shrink-0">
                  {format(new Date(entry.timestamp), 'dd MMM HH:mm')}
                </span>
                <span className="badge-gray">{entry.action}</span>
                <span className="text-gray-600">{entry.username}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
