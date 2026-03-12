/**
 * All Runs list page — sortable, filterable run table.
 */
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { runsApi } from '../../services/api'
import StatusBadge from '../../components/ui/StatusBadge'
import { formatDistanceToNow, format } from 'date-fns'

const STATUSES = [
  'all', 'in_progress', 'awaiting_review', 'completed', 'failed',
]

export default function RunsListPage() {
  const [statusFilter, setStatusFilter] = useState('all')

  const { data: runs = [], isLoading, refetch } = useQuery({
    queryKey: ['runs', statusFilter],
    queryFn: () => runsApi.list({
      limit: 50,
      ...(statusFilter !== 'all' ? { status: statusFilter } : {}),
    }).then((r) => r.data),
    refetchInterval: 15_000,
  })

  return (
    <div className="p-6 space-y-5 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">All Runs</h1>
        <div className="flex gap-3">
          <button onClick={() => refetch()} className="btn-ghost text-sm">🔄 Refresh</button>
          <Link to="/upload" className="btn-primary">+ New Run</Link>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 flex-wrap">
        {STATUSES.map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              statusFilter === s
                ? 'bg-brand-600 text-white'
                : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            {s === 'all' ? 'All' : s.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {['#', 'Run Name', 'Status', 'Progress', 'Created', 'Updated', 'Actions'].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {isLoading ? (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-400">Loading...</td></tr>
              ) : runs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-400">
                    No runs found.{' '}
                    <Link to="/upload" className="text-brand-600 hover:underline">Start one →</Link>
                  </td>
                </tr>
              ) : runs.map((run) => {
                const isActive = ['in_progress', 'queued'].includes(run.status)
                return (
                  <tr key={run.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-gray-400 text-xs">#{run.id}</td>
                    <td className="px-4 py-3">
                      <Link
                        to={isActive ? `/runs/${run.id}/pipeline` : `/runs/${run.id}`}
                        className="font-medium text-gray-800 hover:text-brand-600 transition-colors"
                      >
                        {run.run_name}
                      </Link>
                    </td>
                    <td className="px-4 py-3"><StatusBadge status={run.status} /></td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-gray-200 rounded-full h-1.5">
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
                    <td className="px-4 py-3 text-xs text-gray-500">
                      {format(new Date(run.created_at), 'dd MMM yyyy')}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-400">
                      {formatDistanceToNow(new Date(run.completed_at ?? run.started_at ?? run.created_at ?? ''), { addSuffix: true })}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <Link
                          to={isActive ? `/runs/${run.id}/pipeline` : `/runs/${run.id}`}
                          className="text-xs text-brand-600 hover:underline"
                        >
                          {isActive ? 'Monitor' : 'View'}
                        </Link>
                        {run.status === 'awaiting_review' && (
                          <Link to={`/runs/${run.id}/compliance`} className="text-xs text-yellow-600 hover:underline">
                            Review
                          </Link>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      <p className="text-xs text-gray-400 text-right">Auto-refreshes every 15 seconds</p>
    </div>
  )
}
