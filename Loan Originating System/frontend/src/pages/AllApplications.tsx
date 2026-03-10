import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { Search, RefreshCw } from 'lucide-react'
import { Application } from '../types'
import StatusBadge from '../components/StatusBadge'
import ScoreGauge from '../components/ScoreGauge'

export default function AllApplications() {
  const navigate = useNavigate()
  const [apps, setApps] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const load = async () => {
    setLoading(true)
    const params: any = {}
    if (statusFilter) params.status = statusFilter
    const res = await axios.get('/api/applications', { params })
    setApps(res.data)
    setLoading(false)
  }

  useEffect(() => { load() }, [statusFilter])

  const filtered = apps.filter(a =>
    !search || (a.applicant_name || '').toLowerCase().includes(search.toLowerCase()) ||
    (a.business_name || '').toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">All Applications</h1>
          <p className="text-slate-400 text-sm mt-1">{apps.length} total applications</p>
        </div>
        <button onClick={load} className="btn-secondary flex items-center gap-2">
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            className="input pl-9"
            placeholder="Search by name or business…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <select
          className="input w-44"
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="auto_approved">Approved</option>
          <option value="auto_declined">Declined</option>
          <option value="referred">Under Review</option>
          <option value="fraud_hold">Fraud Hold</option>
          <option value="funded">Funded</option>
        </select>
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-800">
              {['ID', 'Applicant', 'Business', 'Loan Amount', 'Health Score', 'Status', 'Date', 'Actions'].map(h => (
                <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={8} className="text-center py-12 text-slate-500">Loading…</td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan={8} className="text-center py-12 text-slate-500">No applications found.</td></tr>
            ) : (
              filtered.map(app => (
                <tr
                  key={app.id}
                  className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
                >
                  <td className="px-4 py-3 text-sm text-slate-400 font-mono">#{app.id}</td>
                  <td className="px-4 py-3">
                    <div className="text-sm text-white font-medium">{app.applicant_name || '—'}</div>
                    <div className="text-xs text-slate-500">{app.applicant_email || ''}</div>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-300">{app.business_name || '—'}</td>
                  <td className="px-4 py-3 text-sm text-white font-medium">
                    {app.loan_amount ? `$${app.loan_amount.toLocaleString()}` : '—'}
                  </td>
                  <td className="px-4 py-3">
                    {app.health_score != null
                      ? <ScoreGauge score={app.health_score} size="sm" />
                      : <span className="text-slate-600">—</span>
                    }
                  </td>
                  <td className="px-4 py-3"><StatusBadge status={app.status} /></td>
                  <td className="px-4 py-3 text-xs text-slate-500">
                    {new Date(app.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button
                        onClick={() => navigate(`/apply/${app.id}/status`)}
                        className="text-xs text-indigo-400 hover:text-indigo-300"
                      >
                        View
                      </button>
                      {app.status === 'referred' && (
                        <button
                          onClick={() => navigate(`/underwriter/${app.id}`)}
                          className="text-xs text-amber-400 hover:text-amber-300"
                        >
                          Review
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
