import { useState, useEffect } from 'react'
import axios from 'axios'
import { Settings, CheckCircle, AlertTriangle, Lock } from 'lucide-react'
import clsx from 'clsx'
import { ThresholdConfig } from '../types'

export default function AdminSettings() {
  const [config, setConfig] = useState<ThresholdConfig | null>(null)
  const [approveMin, setApproveMin] = useState(700)
  const [declineMax, setDeclineMax] = useState(400)
  const [maxLoan, setMaxLoan] = useState(500000)
  const [minYears, setMinYears] = useState(1.0)
  const [requestedBy, setRequestedBy] = useState('Risk Admin')
  const [approvedBy, setApprovedBy] = useState('Risk Manager')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [approving, setApproving] = useState(false)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => { load() }, [])

  const load = async () => {
    const res = await axios.get('/api/compliance/thresholds')
    setConfig(res.data)
    setApproveMin(res.data.auto_approve_min)
    setDeclineMax(res.data.auto_decline_max)
    setMaxLoan(res.data.max_loan_amount)
    setMinYears(res.data.min_years_in_business)
    setLoading(false)
  }

  const requestUpdate = async () => {
    setSaving(true)
    try {
      const res = await axios.put('/api/compliance/thresholds/request', {
        auto_approve_min: approveMin,
        auto_decline_max: declineMax,
        max_loan_amount: maxLoan,
        min_years_in_business: minYears,
        requested_by: requestedBy,
      })
      setConfig(res.data)
      setSuccess('Threshold update requested. Awaiting second approval (Maker-Checker).')
    } finally {
      setSaving(false)
    }
  }

  const approveUpdate = async () => {
    setApproving(true)
    try {
      const res = await axios.post('/api/compliance/thresholds/approve', {
        approved_by: approvedBy,
      })
      setConfig(res.data)
      setSuccess('Thresholds updated and active in production.')
    } finally {
      setApproving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-3xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Settings className="w-6 h-6 text-indigo-400" />
          Admin — Risk Threshold Management
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Adjust AI decision thresholds. Changes require dual-approval (Maker-Checker workflow).
        </p>
      </div>

      {success && (
        <div className="mb-4 p-3 bg-emerald-900/30 border border-emerald-700 rounded-lg flex items-center gap-2 text-emerald-300 text-sm">
          <CheckCircle className="w-4 h-4" /> {success}
        </div>
      )}

      {/* Current Active Config */}
      <div className="card mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Lock className="w-4 h-4 text-emerald-400" />
          <h2 className="font-semibold text-white">Active Configuration</h2>
          <span className="ml-auto text-xs text-slate-500">Updated by: {config?.updated_by}</span>
        </div>
        <div className="grid grid-cols-2 gap-4">
          {[
            ['Auto-Approve Min Score', config?.auto_approve_min ?? '—'],
            ['Auto-Decline Max Score', config?.auto_decline_max ?? '—'],
            ['Max Loan Amount', config?.max_loan_amount ? `$${config.max_loan_amount.toLocaleString()}` : '—'],
            ['Min Years in Business', config?.min_years_in_business ?? '—'],
          ].map(([label, value]) => (
            <div key={label} className="bg-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-500">{label}</div>
              <div className="text-2xl font-bold text-white mt-1">{value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Score band visualization */}
      <div className="card mb-6">
        <h2 className="font-semibold text-white mb-4">Decision Band Visualization</h2>
        <div className="relative h-8 bg-slate-800 rounded-full overflow-hidden">
          <div
            className="absolute left-0 top-0 bottom-0 bg-red-500/60"
            style={{ width: `${(config?.auto_decline_max ?? 400) / 10}%` }}
          />
          <div
            className="absolute top-0 bottom-0 bg-amber-500/60"
            style={{
              left: `${(config?.auto_decline_max ?? 400) / 10}%`,
              width: `${((config?.auto_approve_min ?? 700) - (config?.auto_decline_max ?? 400)) / 10}%`
            }}
          />
          <div
            className="absolute top-0 bottom-0 bg-emerald-500/60"
            style={{
              left: `${(config?.auto_approve_min ?? 700) / 10}%`,
              right: 0,
            }}
          />
        </div>
        <div className="flex justify-between text-xs text-slate-500 mt-1 px-1">
          <span>0</span>
          <span className="text-red-400">↑ Decline (&lt;{config?.auto_decline_max})</span>
          <span className="text-amber-400">↑ Refer</span>
          <span className="text-emerald-400">↑ Approve (&gt;{config?.auto_approve_min})</span>
          <span>1000</span>
        </div>
      </div>

      {/* Request Update Form */}
      <div className="card mb-4">
        <h2 className="font-semibold text-white mb-4">Request Threshold Update</h2>

        <div className="space-y-5">
          <div>
            <label className="label">
              Auto-Approve Minimum Score: <span className="text-white font-bold">{approveMin}</span>
            </label>
            <input
              type="range" min={500} max={900} step={10}
              value={approveMin}
              onChange={e => setApproveMin(parseInt(e.target.value))}
              className="w-full accent-indigo-500"
            />
            <div className="flex justify-between text-xs text-slate-500">
              <span>500 (lenient)</span><span>900 (strict)</span>
            </div>
          </div>

          <div>
            <label className="label">
              Auto-Decline Maximum Score: <span className="text-white font-bold">{declineMax}</span>
            </label>
            <input
              type="range" min={100} max={600} step={10}
              value={declineMax}
              onChange={e => setDeclineMax(parseInt(e.target.value))}
              className="w-full accent-red-500"
            />
            <div className="flex justify-between text-xs text-slate-500">
              <span>100 (lenient)</span><span>600 (strict)</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Max Loan Amount ($)</label>
              <input
                type="number"
                className="input"
                value={maxLoan}
                onChange={e => setMaxLoan(parseFloat(e.target.value))}
              />
            </div>
            <div>
              <label className="label">Min Years in Business</label>
              <input
                type="number" step="0.5"
                className="input"
                value={minYears}
                onChange={e => setMinYears(parseFloat(e.target.value))}
              />
            </div>
          </div>

          <div>
            <label className="label">Requested By (Maker)</label>
            <input
              type="text" className="input"
              value={requestedBy}
              onChange={e => setRequestedBy(e.target.value)}
            />
          </div>

          {approveMin <= declineMax && (
            <div className="p-3 bg-red-900/20 border border-red-800 rounded-lg text-red-300 text-sm flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              Auto-Approve Min must be greater than Auto-Decline Max.
            </div>
          )}

          <button
            onClick={requestUpdate}
            disabled={saving || approveMin <= declineMax}
            className="btn-primary w-full"
          >
            {saving ? 'Submitting Request…' : 'Submit Change Request (Maker)'}
          </button>
        </div>
      </div>

      {/* Pending Approval (Checker) */}
      {config?.pending_approve_min != null && (
        <div className="card border-amber-700 bg-amber-900/10">
          <div className="flex items-center gap-2 text-amber-300 font-semibold mb-3">
            <AlertTriangle className="w-4 h-4" /> Pending Approval
          </div>
          <div className="text-sm text-slate-300 space-y-1 mb-4">
            <div>New Auto-Approve Min: <strong className="text-white">{config.pending_approve_min}</strong></div>
            <div>New Auto-Decline Max: <strong className="text-white">{config.pending_decline_max}</strong></div>
            <div>Requested By: <strong className="text-white">{config.pending_requested_by}</strong></div>
          </div>

          <div>
            <label className="label">Approver Name (Checker)</label>
            <input
              type="text" className="input mb-3"
              value={approvedBy}
              onChange={e => setApprovedBy(e.target.value)}
            />
          </div>

          <button
            onClick={approveUpdate}
            disabled={approving}
            className="btn-success w-full"
          >
            {approving ? 'Approving…' : 'Approve & Push to Production (Checker)'}
          </button>
        </div>
      )}
    </div>
  )
}
