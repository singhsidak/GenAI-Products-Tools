import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import {
  AlertTriangle, CheckCircle, Info, FileText, ChevronLeft,
  Edit3, Check, X, BarChart2, TrendingUp
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import clsx from 'clsx'
import { Application, Decision, Document, Offer, RiskAlert } from '../types'
import ScoreGauge from '../components/ScoreGauge'
import StatusBadge from '../components/StatusBadge'

interface FullProfile {
  application: Application
  decision: Decision | null
  documents: Document[]
  offers: Offer[]
  risk_alerts: RiskAlert[]
  credit_memo: string
}

type Tab = 'overview' | 'memo' | 'documents' | 'decision'

export default function UnderwriterCopilot() {
  const { appId } = useParams<{ appId: string }>()
  const navigate = useNavigate()
  const [profile, setProfile] = useState<FullProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState<Tab>('overview')
  const [showDecisionModal, setShowDecisionModal] = useState(false)
  const [decisionType, setDecisionType] = useState<'manual_approve' | 'manual_decline' | 'request_more_info'>('manual_approve')
  const [decisionNotes, setDecisionNotes] = useState('')
  const [finalRate, setFinalRate] = useState('')
  const [finalAmount, setFinalAmount] = useState('')
  const [finalTerm, setFinalTerm] = useState('24')
  const [declineReasons, setDeclineReasons] = useState<string[]>([])
  const [submittingDecision, setSubmittingDecision] = useState(false)
  const [memoText, setMemoText] = useState('')
  const [editingMemo, setEditingMemo] = useState(false)

  useEffect(() => {
    if (appId) load()
  }, [appId])

  const load = async () => {
    setLoading(true)
    try {
      const res = await axios.get(`/api/underwriter/${appId}/full`)
      setProfile(res.data)
      setMemoText(res.data.credit_memo)
      if (res.data.application.loan_amount) setFinalAmount(String(res.data.application.loan_amount))
    } finally {
      setLoading(false)
    }
  }

  const submitDecision = async () => {
    setSubmittingDecision(true)
    try {
      await axios.post(`/api/decisions/${appId}/manual`, {
        decision_type: decisionType,
        notes: decisionNotes,
        final_rate: finalRate ? parseFloat(finalRate) : null,
        final_amount: finalAmount ? parseFloat(finalAmount) : null,
        final_term_months: finalTerm ? parseInt(finalTerm) : null,
        decline_reasons: declineReasons.length > 0 ? declineReasons : null,
        decided_by: 'Underwriter',
      })
      setShowDecisionModal(false)
      navigate('/underwriter')
    } finally {
      setSubmittingDecision(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!profile) return <div className="p-8 text-slate-400">Not found.</div>

  const { application: app, decision, documents, risk_alerts } = profile
  const shap = decision?.shap_values ?? {}
  const shapData = Object.entries(shap)
    .map(([k, v]) => ({ name: k.replace(/_/g, ' '), value: v, pos: v >= 0 }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))

  const alertIcon = (sev: string) => {
    if (sev === 'high') return <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0" />
    if (sev === 'medium') return <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
    return <Info className="w-4 h-4 text-blue-400 flex-shrink-0" />
  }

  const DECLINE_OPTIONS = [
    'Insufficient credit history',
    'Debt-to-income ratio too high',
    'Insufficient time in business',
    'Requested amount exceeds revenue capacity',
    'NSF frequency indicates liquidity risk',
    'Unresolved document discrepancies',
  ]

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="border-b border-slate-800 px-6 py-4 flex items-center gap-4 flex-shrink-0">
        <button onClick={() => navigate('/underwriter')} className="text-slate-400 hover:text-white transition-colors">
          <ChevronLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="font-bold text-white">{app.applicant_name} — {app.business_name}</h1>
            <StatusBadge status={app.status} />
          </div>
          <div className="text-sm text-slate-400">
            #{app.id} • {app.business_type} • {app.industry} • {app.state}
          </div>
        </div>
        {app.health_score != null && <ScoreGauge score={app.health_score} size="sm" />}
        <button
          onClick={() => setShowDecisionModal(true)}
          className="btn-primary"
        >
          Make Decision
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800 px-6 flex gap-1 flex-shrink-0">
        {(['overview', 'memo', 'documents', 'decision'] as Tab[]).map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={clsx(
              'px-4 py-3 text-sm font-medium capitalize border-b-2 transition-colors -mb-px',
              tab === t
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            )}
          >
            {t === 'memo' ? 'AI Credit Memo' : t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">

        {/* OVERVIEW TAB */}
        {tab === 'overview' && (
          <div className="p-6 grid grid-cols-3 gap-4">
            {/* Left: Risk Alerts */}
            <div className="col-span-1 space-y-4">
              <div className="card">
                <h2 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" /> Risk Alerts
                </h2>
                <div className="space-y-3">
                  {risk_alerts.map((a, i) => (
                    <div key={i} className={clsx(
                      'p-3 rounded-lg border text-sm flex gap-2',
                      a.severity === 'high' ? 'bg-red-900/20 border-red-800' :
                      a.severity === 'medium' ? 'bg-amber-900/20 border-amber-800' :
                      'bg-blue-900/10 border-blue-900'
                    )}>
                      {alertIcon(a.severity)}
                      <div>
                        <div className={clsx(
                          'font-medium text-xs mb-0.5',
                          a.severity === 'high' ? 'text-red-300' :
                          a.severity === 'medium' ? 'text-amber-300' :
                          'text-blue-300'
                        )}>{a.code}</div>
                        <div className="text-slate-300 text-xs">{a.message}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* SHAP chart */}
              {shapData.length > 0 && (
                <div className="card">
                  <h2 className="font-semibold text-white mb-3 flex items-center gap-2">
                    <BarChart2 className="w-4 h-4 text-indigo-400" /> SHAP Factors
                  </h2>
                  <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={shapData} layout="vertical">
                      <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} />
                      <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} width={110} />
                      <Tooltip
                        contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8 }}
                        labelStyle={{ color: '#e2e8f0' }}
                        itemStyle={{ color: '#a5b4fc' }}
                      />
                      <Bar dataKey="value" radius={3}>
                        {shapData.map((d, i) => (
                          <Cell key={i} fill={d.pos ? '#10b981' : '#ef4444'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Right: Financial Summary */}
            <div className="col-span-2 space-y-4">
              <div className="card">
                <h2 className="font-semibold text-white mb-4">Financial Profile</h2>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    ['Annual Revenue', app.annual_revenue ? `$${app.annual_revenue.toLocaleString()}` : '—'],
                    ['Monthly Expenses', app.monthly_expenses ? `$${app.monthly_expenses.toLocaleString()}` : '—'],
                    ['Credit Score', app.credit_score || '—'],
                    ['Years in Business', app.years_in_business || '—'],
                    ['Loan Requested', app.loan_amount ? `$${app.loan_amount.toLocaleString()}` : '—'],
                    ['Loan Purpose', app.loan_purpose || '—'],
                    ['Avg Bank Balance', app.avg_bank_balance ? `$${app.avg_bank_balance.toLocaleString()}` : '—'],
                    ['NSF Count (12mo)', app.nsf_count],
                    ['Bank Connected', app.bank_connected ? '✓ Yes' : '✗ No'],
                    ['Monthly Deposits', app.monthly_deposits_avg ? `$${app.monthly_deposits_avg.toLocaleString()}` : '—'],
                  ].map(([label, value]) => (
                    <div key={label} className="bg-slate-800/50 rounded-lg p-3">
                      <div className="text-xs text-slate-500">{label}</div>
                      <div className="text-sm font-semibold text-white mt-0.5">{value}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* DTI Gauge */}
              {app.annual_revenue && app.monthly_expenses && (
                <div className="card">
                  <h2 className="font-semibold text-white mb-3">Key Ratios</h2>
                  <div className="space-y-3">
                    {[
                      {
                        label: 'Debt-to-Income (DTI)',
                        value: Math.min(100, Math.round((app.monthly_expenses * 12 / app.annual_revenue) * 100)),
                        threshold: 50,
                        format: (v: number) => `${v}%`,
                      },
                      {
                        label: 'Loan-to-Revenue (LTR)',
                        value: Math.min(100, Math.round(((app.loan_amount || 0) / app.annual_revenue) * 100)),
                        threshold: 60,
                        format: (v: number) => `${v}%`,
                      },
                    ].map(({ label, value, threshold, format }) => (
                      <div key={label}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-slate-400">{label}</span>
                          <span className={value > threshold ? 'text-red-400' : 'text-emerald-400'} >
                            {format(value)}
                          </span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className={clsx('h-full rounded-full transition-all', value > threshold ? 'bg-red-500' : 'bg-emerald-500')}
                            style={{ width: `${value}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* MEMO TAB */}
        {tab === 'memo' && (
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-white flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-indigo-400" />
                AI-Generated Credit Memo
              </h2>
              <button
                onClick={() => setEditingMemo(e => !e)}
                className="btn-secondary flex items-center gap-2 text-sm"
              >
                <Edit3 className="w-3 h-3" />
                {editingMemo ? 'Preview' : 'Edit'}
              </button>
            </div>
            {editingMemo ? (
              <textarea
                className="input w-full font-mono text-sm"
                rows={40}
                value={memoText}
                onChange={e => setMemoText(e.target.value)}
              />
            ) : (
              <div className="card dark-prose max-w-none prose prose-invert">
                <ReactMarkdown>{memoText}</ReactMarkdown>
              </div>
            )}
          </div>
        )}

        {/* DOCUMENTS TAB */}
        {tab === 'documents' && (
          <div className="p-6 space-y-3">
            <h2 className="font-semibold text-white mb-4">Submitted Documents</h2>
            {documents.length === 0 ? (
              <div className="text-slate-500 text-center py-12">No documents uploaded.</div>
            ) : documents.map(doc => (
              <div key={doc.id} className="card flex items-start gap-4">
                <div className={clsx(
                  'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0',
                  doc.status === 'flagged' ? 'bg-red-900' : 'bg-emerald-900'
                )}>
                  <FileText className={clsx('w-5 h-5', doc.status === 'flagged' ? 'text-red-400' : 'text-emerald-400')} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-white">{doc.doc_type.replace('_', ' ').toUpperCase()}</span>
                    {doc.status === 'flagged' && (
                      <span className="text-xs bg-red-900 text-red-300 px-2 py-0.5 rounded-full">
                        Tamper: {doc.tamper_score.toFixed(1)}%
                      </span>
                    )}
                    {doc.status === 'processed' && (
                      <span className="text-xs bg-emerald-900 text-emerald-300 px-2 py-0.5 rounded-full">
                        Verified
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-slate-400">{doc.filename}</div>
                  {doc.extracted_data && (
                    <div className="mt-2 grid grid-cols-2 gap-2">
                      {Object.entries(doc.extracted_data).map(([k, v]) => (
                        <div key={k} className="bg-slate-800 rounded px-2 py-1 text-xs">
                          <span className="text-slate-500">{k}: </span>
                          <span className="text-slate-200 font-medium">{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* DECISION TAB */}
        {tab === 'decision' && (
          <div className="p-6 space-y-4">
            <h2 className="font-semibold text-white mb-4">AI Decision Details</h2>
            {decision ? (
              <>
                <div className="card">
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <div className="text-slate-500">Decision Type</div>
                      <div className="text-white font-semibold mt-0.5">{decision.decision_type.replace(/_/g, ' ').toUpperCase()}</div>
                    </div>
                    <div>
                      <div className="text-slate-500">Decided By</div>
                      <div className="text-white font-semibold mt-0.5 capitalize">{decision.decided_by}</div>
                    </div>
                    <div>
                      <div className="text-slate-500">Decision Time</div>
                      <div className="text-white font-semibold mt-0.5">{new Date(decision.decided_at).toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-slate-500">Health Score</div>
                      <div className="text-white font-semibold mt-0.5">{app.health_score ?? '—'} / 1000</div>
                    </div>
                  </div>
                </div>
                {decision.reasons && (
                  <div className="card">
                    <h3 className="font-medium text-white mb-2">Decision Reasons</h3>
                    {decision.reasons.map((r, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm text-slate-300 mb-2">
                        <span className="mt-1.5 w-1.5 h-1.5 bg-indigo-400 rounded-full flex-shrink-0" />
                        {r}
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <div className="text-slate-500 text-center py-12">No AI decision recorded yet.</div>
            )}

            <button onClick={() => setShowDecisionModal(true)} className="btn-primary">
              Override / Make Final Decision
            </button>
          </div>
        )}
      </div>

      {/* Decision Modal */}
      {showDecisionModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-white">Final Decision</h2>
              <button onClick={() => setShowDecisionModal(false)} className="text-slate-500 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Decision type */}
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'manual_approve', label: 'Approve', cls: 'border-emerald-500 bg-emerald-900/20 text-emerald-300' },
                { value: 'manual_decline', label: 'Decline', cls: 'border-red-500 bg-red-900/20 text-red-300' },
                { value: 'request_more_info', label: 'More Info', cls: 'border-amber-500 bg-amber-900/20 text-amber-300' },
              ].map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setDecisionType(opt.value as any)}
                  className={clsx(
                    'py-2 rounded-lg border text-sm font-medium transition-all',
                    decisionType === opt.value ? opt.cls : 'border-slate-700 text-slate-400'
                  )}
                >
                  {opt.label}
                </button>
              ))}
            </div>

            {/* Approve fields */}
            {decisionType === 'manual_approve' && (
              <div className="space-y-3">
                <div>
                  <label className="label">Final Amount ($)</label>
                  <input className="input" type="number" value={finalAmount} onChange={e => setFinalAmount(e.target.value)} />
                </div>
                <div>
                  <label className="label">Interest Rate (APR %)</label>
                  <input className="input" type="number" step="0.1" value={finalRate} onChange={e => setFinalRate(e.target.value)} placeholder="8.5" />
                </div>
                <div>
                  <label className="label">Term (months)</label>
                  <input className="input" type="number" value={finalTerm} onChange={e => setFinalTerm(e.target.value)} />
                </div>
              </div>
            )}

            {/* Decline fields */}
            {decisionType === 'manual_decline' && (
              <div className="space-y-2">
                <label className="label">Select Decline Reasons</label>
                {DECLINE_OPTIONS.map(opt => (
                  <label key={opt} className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={declineReasons.includes(opt)}
                      onChange={e => setDeclineReasons(prev =>
                        e.target.checked ? [...prev, opt] : prev.filter(r => r !== opt)
                      )}
                      className="rounded border-slate-600"
                    />
                    {opt}
                  </label>
                ))}
              </div>
            )}

            {/* Notes */}
            <div>
              <label className="label">Underwriter Notes</label>
              <textarea
                className="input resize-none"
                rows={3}
                value={decisionNotes}
                onChange={e => setDecisionNotes(e.target.value)}
                placeholder="Add notes for the audit trail…"
              />
            </div>

            <div className="flex gap-3">
              <button onClick={() => setShowDecisionModal(false)} className="btn-secondary flex-1">
                Cancel
              </button>
              <button
                onClick={submitDecision}
                disabled={submittingDecision}
                className={clsx(
                  'flex-1 flex items-center justify-center gap-2',
                  decisionType === 'manual_approve' ? 'btn-success' :
                  decisionType === 'manual_decline' ? 'btn-danger' :
                  'btn-primary'
                )}
              >
                {submittingDecision ? 'Submitting…' : (
                  <><Check className="w-4 h-4" /> Confirm</>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
