import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { Clock, TrendingUp, AlertCircle, ChevronRight, Users } from 'lucide-react'
import { Application } from '../types'
import ScoreGauge from '../components/ScoreGauge'

function timeInQueue(createdAt: string) {
  const diff = Date.now() - new Date(createdAt).getTime()
  const hours = Math.floor(diff / 3600000)
  const mins = Math.floor((diff % 3600000) / 60000)
  if (hours > 24) return `${Math.floor(hours / 24)}d ${hours % 24}h`
  if (hours > 0) return `${hours}h ${mins}m`
  return `${mins}m`
}

export default function UnderwriterDashboard() {
  const navigate = useNavigate()
  const [queue, setQueue] = useState<Application[]>([])
  const [stats, setStats] = useState<{ queue_count: number; avg_health_score: number; sla_warning_count: number } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      axios.get('/api/underwriter/queue'),
      axios.get('/api/underwriter/stats'),
    ]).then(([q, s]) => {
      setQueue(q.data)
      setStats(s.data)
    }).finally(() => setLoading(false))
  }, [])

  const slaColor = (createdAt: string) => {
    const hours = (Date.now() - new Date(createdAt).getTime()) / 3600000
    if (hours > 48) return 'text-red-400'
    if (hours > 24) return 'text-amber-400'
    return 'text-emerald-400'
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Underwriter Queue</h1>
        <p className="text-slate-400 text-sm mt-1">Applications referred for human review</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          {
            icon: <Users className="w-5 h-5 text-indigo-400" />,
            label: 'In Queue',
            value: stats?.queue_count ?? '—',
            bg: 'bg-indigo-900/20 border-indigo-800',
          },
          {
            icon: <TrendingUp className="w-5 h-5 text-amber-400" />,
            label: 'Avg Health Score',
            value: stats?.avg_health_score ?? '—',
            bg: 'bg-amber-900/20 border-amber-800',
          },
          {
            icon: <AlertCircle className="w-5 h-5 text-red-400" />,
            label: 'SLA Warning',
            value: stats?.sla_warning_count ?? '—',
            bg: 'bg-red-900/20 border-red-800',
          },
        ].map(({ icon, label, value, bg }) => (
          <div key={label} className={`card flex items-center gap-4 border ${bg}`}>
            <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0">
              {icon}
            </div>
            <div>
              <div className="text-2xl font-bold text-white">{value}</div>
              <div className="text-sm text-slate-400">{label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Queue */}
      <div className="card p-0 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="font-semibold text-white">Referred Applications</h2>
          <span className="text-xs text-slate-500">Sorted by oldest first (SLA priority)</span>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-500">Loading queue…</div>
        ) : queue.length === 0 ? (
          <div className="py-16 text-center">
            <div className="text-4xl mb-3">✅</div>
            <div className="text-slate-400">Queue is clear — no referred applications.</div>
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {queue.map(app => {
              const waitTime = timeInQueue(app.created_at)
              const waitClass = slaColor(app.created_at)
              return (
                <div
                  key={app.id}
                  className="flex items-center gap-4 px-6 py-4 hover:bg-slate-800/30 cursor-pointer transition-colors"
                  onClick={() => navigate(`/underwriter/${app.id}`)}
                >
                  {/* Score */}
                  {app.health_score != null
                    ? <ScoreGauge score={app.health_score} size="sm" />
                    : <div className="w-16 h-16 bg-slate-800 rounded-full" />
                  }

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <div className="font-semibold text-white">{app.applicant_name || `Application #${app.id}`}</div>
                      {app.bank_connected && (
                        <span className="text-xs bg-indigo-900 text-indigo-300 px-2 py-0.5 rounded-full">Bank ✓</span>
                      )}
                    </div>
                    <div className="text-sm text-slate-400">{app.business_name || '—'} • {app.business_type}</div>
                    <div className="text-xs text-slate-500 mt-0.5">{app.industry} • {app.state}</div>
                  </div>

                  {/* Loan */}
                  <div className="text-right hidden md:block">
                    <div className="font-semibold text-white">${(app.loan_amount || 0).toLocaleString()}</div>
                    <div className="text-xs text-slate-400">{app.loan_purpose}</div>
                  </div>

                  {/* Wait time */}
                  <div className="text-right hidden md:block w-20">
                    <div className={`font-semibold text-sm ${waitClass}`}>{waitTime}</div>
                    <div className="text-xs text-slate-500 flex items-center justify-end gap-1">
                      <Clock className="w-3 h-3" /> in queue
                    </div>
                  </div>

                  <ChevronRight className="w-5 h-5 text-slate-600 flex-shrink-0" />
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
