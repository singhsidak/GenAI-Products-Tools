/**
 * S-04 Dashboard — analytics summary + recent runs list.
 * Stitch MCP provides analytics; local API provides run list.
 */
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { dashboardApi, runsApi } from '../../services/api'
import StatusBadge from '../../components/ui/StatusBadge'
import { formatDistanceToNow, format } from 'date-fns'
import { useAuthStore } from '../../store/authStore'

function StatCard({ label, value, sub, color = 'text-gray-900' }: {
  label: string; value: string | number; sub?: string; color?: string
}) {
  return (
    <div className="card p-5">
      <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">{label}</p>
      <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const isAdmin = user?.role === 'admin'

  const { data: analytics } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => dashboardApi.getAnalytics().then((r) => r.data),
    enabled: isAdmin,
  })

  const { data: runs = [] } = useQuery({
    queryKey: ['runs'],
    queryFn: () => runsApi.list({ limit: 20 }).then((r) => r.data),
    refetchInterval: 30_000,
  })

  const passRate = analytics?.compliance_pass_rate
    ? `${(analytics.compliance_pass_rate * 100).toFixed(0)}%`
    : '—'

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">
            {format(new Date(), 'EEEE, dd MMMM yyyy')}
          </p>
        </div>
        <Link to="/upload" className="btn-primary">
          + New Run
        </Link>
      </div>

      {/* Stats (admin only) */}
      {isAdmin && analytics && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total Runs" value={analytics.total_runs} />
          <StatCard
            label="Avg Completion"
            value={analytics.avg_completion_minutes ? `${analytics.avg_completion_minutes.toFixed(0)}m` : '—'}
            sub="per pipeline run"
          />
          <StatCard
            label="Compliance Pass Rate"
            value={passRate}
            color={analytics.compliance_pass_rate && analytics.compliance_pass_rate > 0.8 ? 'text-green-600' : 'text-yellow-600'}
          />
          <StatCard
            label="Total Tokens Used"
            value={analytics.total_tokens_used?.toLocaleString() ?? '0'}
            sub={`Est. $${analytics.total_cost_usd?.toFixed(2) ?? '0.00'}`}
          />
        </div>
      )}

      {/* Status breakdown (admin only) */}
      {isAdmin && analytics?.runs_by_status && (
        <div className="card p-5">
          <h2 className="font-semibold text-gray-700 text-sm mb-3">Runs by Status</h2>
          <div className="flex gap-3 flex-wrap">
            {Object.entries(analytics.runs_by_status).map(([status, count]) => (
              <div key={status} className="flex items-center gap-2">
                <StatusBadge status={status} />
                <span className="text-sm font-medium text-gray-700">{count as number}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Runs table */}
      <div className="card overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="font-semibold text-gray-700 text-sm">Recent Runs</h2>
          <Link to="/runs" className="text-xs text-brand-600 hover:underline">View all →</Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {['Run Name', 'Status', 'Sections', 'Started', ''].map((h) => (
                  <th key={h} className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {runs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-5 py-10 text-center text-gray-400">
                    No runs yet.{' '}
                    <Link to="/upload" className="text-brand-600 hover:underline">Start your first run →</Link>
                  </td>
                </tr>
              ) : (
                runs.map((run) => (
                  <tr key={run.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-5 py-3">
                      <Link to={`/runs/${run.id}`} className="font-medium text-gray-800 hover:text-brand-600 transition-colors">
                        {run.run_name}
                      </Link>
                      <p className="text-xs text-gray-400">#{run.id}</p>
                    </td>
                    <td className="px-5 py-3">
                      <StatusBadge status={run.status} />
                    </td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-gray-200 rounded-full h-1.5">
                          <div
                            className="h-full bg-brand-500 rounded-full"
                            style={{ width: `${((run.completed_sections ?? 0) / Math.max(run.total_sections ?? 16, 1)) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500">
                          {run.completed_sections ?? 0}/{run.total_sections ?? 16}
                        </span>
                      </div>
                    </td>
                    <td className="px-5 py-3 text-gray-500 text-xs">
                      {formatDistanceToNow(new Date(run.created_at), { addSuffix: true })}
                    </td>
                    <td className="px-5 py-3">
                      <Link
                        to={['in_progress', 'queued'].includes(run.status)
                          ? `/runs/${run.id}/pipeline`
                          : `/runs/${run.id}`
                        }
                        className="text-xs text-brand-600 hover:underline"
                      >
                        {['in_progress', 'queued'].includes(run.status) ? 'Monitor →' : 'View →'}
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
