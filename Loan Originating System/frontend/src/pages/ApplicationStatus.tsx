import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { CheckCircle, XCircle, Clock, AlertTriangle, TrendingUp, ChevronRight } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import clsx from 'clsx'
import { Application, Decision, Offer } from '../types'
import ScoreGauge from '../components/ScoreGauge'

export default function ApplicationStatus() {
  const { appId } = useParams<{ appId: string }>()
  const navigate = useNavigate()
  const [app, setApp] = useState<Application | null>(null)
  const [decision, setDecision] = useState<Decision | null>(null)
  const [offers, setOffers] = useState<Offer[]>([])
  const [loading, setLoading] = useState(true)
  const [accepting, setAccepting] = useState<number | null>(null)
  const [accepted, setAccepted] = useState(false)

  useEffect(() => {
    if (appId) load(parseInt(appId))
  }, [appId])

  const load = async (id: number) => {
    try {
      const [appRes, decRes, offRes] = await Promise.allSettled([
        axios.get(`/api/applications/${id}`),
        axios.get(`/api/decisions/${id}`),
        axios.get(`/api/offers/${id}`),
      ])
      if (appRes.status === 'fulfilled') setApp(appRes.value.data)
      if (decRes.status === 'fulfilled') setDecision(decRes.value.data)
      if (offRes.status === 'fulfilled') setOffers(offRes.value.data)
    } finally {
      setLoading(false)
    }
  }

  const acceptOffer = async (offerId: number) => {
    if (!appId) return
    setAccepting(offerId)
    await axios.post(`/api/offers/${appId}/accept/${offerId}`)
    setAccepted(true)
    await load(parseInt(appId))
    setAccepting(null)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center space-y-3">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <div className="text-slate-400">Loading decision…</div>
        </div>
      </div>
    )
  }

  if (!app) return <div className="p-8 text-slate-400">Application not found.</div>

  const isApproved = app.status === 'auto_approved' || app.status === 'funded'
  const isDeclined = app.status === 'auto_declined'
  const isReferred = app.status === 'referred'
  const isFraud = app.status === 'fraud_hold'
  const isFunded = app.status === 'funded'

  const shap = decision?.shap_values ?? {}
  const shapData = Object.entries(shap)
    .map(([k, v]) => ({ name: k.replace(/_/g, ' '), value: v, positive: v >= 0 }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, 6)

  const productLabels: Record<string, string> = {
    term_loan: 'Term Loan',
    line_of_credit: 'Line of Credit',
    sba_loan: 'SBA Loan',
  }

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      {/* Decision Banner */}
      <div className={clsx(
        'rounded-2xl p-6 flex items-start gap-5',
        isApproved && !isFunded ? 'bg-emerald-900/30 border border-emerald-700' :
        isFunded ? 'bg-emerald-900/40 border border-emerald-500' :
        isDeclined ? 'bg-red-900/30 border border-red-700' :
        isFraud ? 'bg-rose-900/30 border border-rose-700' :
        'bg-amber-900/20 border border-amber-700'
      )}>
        <div className={clsx(
          'w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0',
          isApproved ? 'bg-emerald-500/20' : isDeclined ? 'bg-red-500/20' :
          isFraud ? 'bg-rose-500/20' : 'bg-amber-500/20'
        )}>
          {isApproved ? <CheckCircle className="w-7 h-7 text-emerald-400" /> :
           isDeclined ? <XCircle className="w-7 h-7 text-red-400" /> :
           isFraud ? <AlertTriangle className="w-7 h-7 text-rose-400" /> :
           <Clock className="w-7 h-7 text-amber-400" />}
        </div>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-white">
            {isFunded ? 'Loan Funded!' :
             isApproved ? 'Congratulations — You\'re Pre-Approved!' :
             isDeclined ? 'Application Not Approved' :
             isFraud ? 'Application On Hold — Document Review Required' :
             'Under Review — Referred to Underwriter'}
          </h1>
          <p className={clsx('mt-1 text-sm',
            isApproved ? 'text-emerald-300' : isDeclined ? 'text-red-300' :
            isFraud ? 'text-rose-300' : 'text-amber-300'
          )}>
            {isFunded ? 'Your loan has been disbursed. Funds should arrive within 1–2 business days.' :
             isApproved ? 'Select one of the offers below to proceed to e-signature.' :
             isDeclined ? 'Please review the reasons below. You may reapply in 90 days.' :
             isFraud ? 'A document flagged for review. Our fraud team will contact you within 24 hours.' :
             'A human underwriter is reviewing your file. Expected response: 1–2 business days.'}
          </p>
          <div className="mt-3 text-xs text-slate-500">
            Application #{app.id} • {app.applicant_name} • {new Date(app.created_at).toLocaleDateString()}
          </div>
        </div>
        {app.health_score != null && (
          <ScoreGauge score={app.health_score} />
        )}
      </div>

      {/* Offers */}
      {isApproved && offers.length > 0 && !isFunded && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Select Your Loan Offer</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {offers.map((offer, i) => (
              <div key={offer.id} className={clsx(
                'p-4 rounded-xl border transition-all',
                i === 1 ? 'border-indigo-500 bg-indigo-900/20' : 'border-slate-700 bg-slate-800'
              )}>
                {i === 1 && (
                  <div className="text-xs text-indigo-400 font-semibold mb-2">RECOMMENDED</div>
                )}
                <div className="text-sm font-semibold text-white mb-3">
                  {productLabels[offer.product_type] || offer.product_type}
                </div>
                <div className="space-y-2 text-sm mb-4">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Amount</span>
                    <span className="text-white font-semibold">${offer.amount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">APR</span>
                    <span className="text-white font-semibold">{offer.rate}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Term</span>
                    <span className="text-white">{offer.term_months} months</span>
                  </div>
                  <div className="flex justify-between border-t border-slate-700 pt-2">
                    <span className="text-slate-400">Monthly</span>
                    <span className="text-emerald-400 font-bold">${offer.monthly_payment.toFixed(0)}</span>
                  </div>
                </div>
                <button
                  onClick={() => acceptOffer(offer.id)}
                  disabled={accepting !== null}
                  className={clsx('w-full py-2 rounded-lg text-sm font-medium transition-colors',
                    i === 1
                      ? 'bg-indigo-600 hover:bg-indigo-500 text-white'
                      : 'bg-slate-700 hover:bg-slate-600 text-slate-200'
                  )}
                >
                  {accepting === offer.id ? 'Processing…' : 'Select & E-Sign'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Funded confirmation */}
      {isFunded && (
        <div className="card flex flex-col items-center text-center py-8">
          <div className="text-5xl mb-4">🎉</div>
          <h2 className="text-xl font-bold text-white">Your loan has been funded!</h2>
          <p className="text-slate-400 text-sm mt-2">Funds will arrive via ACH within 1–2 business days.</p>
        </div>
      )}

      {/* SHAP Explainability */}
      {decision?.shap_values && shapData.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-semibold text-white">AI Decision Factors</h2>
            <span className="text-xs text-slate-500 ml-auto">SHAP Explainability</span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={shapData} layout="vertical" margin={{ left: 20 }}>
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} width={130} />
              <Tooltip
                contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8 }}
                labelStyle={{ color: '#e2e8f0' }}
                itemStyle={{ color: '#a5b4fc' }}
              />
              <Bar dataKey="value" radius={4}>
                {shapData.map((d, i) => (
                  <Cell key={i} fill={d.positive ? '#10b981' : '#ef4444'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Decline Reasons / Adverse Action */}
      {isDeclined && decision && (
        <div className="card space-y-3">
          <h2 className="text-lg font-semibold text-white">Reasons for Decline</h2>
          {decision.reasons?.map((r, i) => (
            <div key={i} className="flex items-start gap-2 text-sm text-red-300">
              <span className="mt-1 w-1.5 h-1.5 bg-red-400 rounded-full flex-shrink-0" />
              {r}
            </div>
          ))}
          {decision.adverse_action_codes && (
            <>
              <div className="border-t border-slate-800 pt-3">
                <div className="text-sm font-medium text-slate-300 mb-2">ECOA/FCRA Adverse Action Codes:</div>
                {decision.adverse_action_codes.map((c, i) => (
                  <div key={i} className="text-sm text-slate-400 font-mono">{c}</div>
                ))}
              </div>
              <button
                onClick={() => navigate(`/api/decisions/${app.id}/adverse-action`)}
                className="text-sm text-indigo-400 hover:text-indigo-300 underline"
              >
                Download Adverse Action Notice (PDF)
              </button>
            </>
          )}
        </div>
      )}

      {/* CTA */}
      {!isApproved && !isFunded && (
        <div className="flex justify-center gap-3">
          <button onClick={() => navigate('/apply')} className="btn-secondary">
            Start New Application
          </button>
          <button onClick={() => navigate(`/apply/${app.id}/documents`)} className="btn-primary flex items-center gap-2">
            Upload Documents <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  )
}
