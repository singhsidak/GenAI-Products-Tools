import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { CheckCircle, ChevronRight, ChevronLeft, Building2, Wifi, AlertCircle } from 'lucide-react'
import clsx from 'clsx'

const BUSINESS_TYPES = [
  { value: 'sole_proprietor', label: 'Sole Proprietor', desc: 'You and your business are the same entity' },
  { value: 'llc', label: 'LLC', desc: 'Limited Liability Company' },
  { value: 'corporation', label: 'Corporation', desc: 'C-Corp or S-Corp' },
  { value: 'partnership', label: 'Partnership', desc: 'General or Limited Partnership' },
]

const INDUSTRIES = [
  'Retail', 'Restaurant / Food Service', 'Healthcare', 'Technology',
  'Construction', 'Manufacturing', 'Professional Services', 'Transportation',
  'Real Estate', 'Education', 'Other',
]

const LOAN_PURPOSES = [
  'Working Capital', 'Equipment Purchase', 'Inventory', 'Business Expansion',
  'Hire Staff', 'Marketing', 'Debt Consolidation', 'Other',
]

const US_STATES = [
  'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN',
  'IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV',
  'NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN',
  'TX','UT','VT','VA','WA','WV','WI','WY',
]

interface FormData {
  applicant_name: string
  applicant_email: string
  applicant_phone: string
  business_name: string
  business_type: string
  ein: string
  years_in_business: string
  industry: string
  state: string
  annual_revenue: string
  monthly_expenses: string
  credit_score: string
  existing_debt: string
  loan_amount: string
  loan_purpose: string
}

const INITIAL: FormData = {
  applicant_name: '', applicant_email: '', applicant_phone: '',
  business_name: '', business_type: '', ein: '', years_in_business: '',
  industry: '', state: '', annual_revenue: '', monthly_expenses: '',
  credit_score: '', existing_debt: '', loan_amount: '', loan_purpose: '',
}

type Step = 'business_type' | 'personal' | 'business' | 'financials' | 'loan' | 'bank' | 'review'

const STEPS: Step[] = ['business_type', 'personal', 'business', 'financials', 'loan', 'bank', 'review']
const STEP_LABELS: Record<Step, string> = {
  business_type: 'Business Type',
  personal: 'Personal Info',
  business: 'Business Details',
  financials: 'Financials',
  loan: 'Loan Request',
  bank: 'Bank Connect',
  review: 'Review & Submit',
}

export default function BorrowerApplication() {
  const navigate = useNavigate()
  const [step, setStep] = useState<Step>('business_type')
  const [form, setForm] = useState<FormData>(INITIAL)
  const [appId, setAppId] = useState<number | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [bankConnecting, setBankConnecting] = useState(false)
  const [bankConnected, setBankConnected] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const stepIdx = STEPS.indexOf(step)
  const isSoleProprietor = form.business_type === 'sole_proprietor'

  const set = (k: keyof FormData, v: string) => setForm(f => ({ ...f, [k]: v }))

  // Auto-save on step change
  const saveProgress = async () => {
    try {
      const payload: Record<string, any> = {}
      for (const [k, v] of Object.entries(form)) {
        if (v !== '') {
          if (['years_in_business', 'annual_revenue', 'monthly_expenses', 'credit_score', 'existing_debt', 'loan_amount'].includes(k)) {
            payload[k] = parseFloat(v)
          } else {
            payload[k] = v
          }
        }
      }
      if (appId) {
        await axios.put(`/api/applications/${appId}`, payload)
      } else {
        const res = await axios.post('/api/applications', payload)
        setAppId(res.data.id)
        setSessionId(res.data.session_id)
      }
    } catch (e) { /* silent */ }
  }

  const next = async () => {
    setError(null)
    await saveProgress()
    const idx = STEPS.indexOf(step)
    if (idx < STEPS.length - 1) setStep(STEPS[idx + 1])
  }

  const back = () => {
    const idx = STEPS.indexOf(step)
    if (idx > 0) setStep(STEPS[idx - 1])
  }

  const connectBank = async () => {
    if (!appId) return
    setBankConnecting(true)
    try {
      await new Promise(r => setTimeout(r, 2200)) // simulate Plaid loading
      await axios.post(`/api/applications/${appId}/bank-connect`)
      setBankConnected(true)
    } catch {
      setError('Bank connection failed. Please try again.')
    } finally {
      setBankConnecting(false)
    }
  }

  const submit = async () => {
    if (!appId) return
    setSubmitting(true)
    setError(null)
    try {
      const res = await axios.post(`/api/applications/${appId}/submit`)
      navigate(`/apply/${appId}/status`)
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Submission failed. Please fill all required fields.')
      setSubmitting(false)
    }
  }

  const Field = ({ label, name, type = 'text', placeholder = '', required = false, children }: any) => (
    <div>
      <label className="label">{label}{required && <span className="text-red-400 ml-1">*</span>}</label>
      {children ?? (
        <input
          type={type}
          className="input"
          placeholder={placeholder}
          value={form[name as keyof FormData]}
          onChange={e => set(name, e.target.value)}
        />
      )}
    </div>
  )

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <div className="border-b border-slate-800 px-8 py-4 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-white">New Loan Application</h1>
        {sessionId && (
          <span className="text-xs text-slate-500">Session: {sessionId.slice(0, 8)}…</span>
        )}
      </div>

      {/* Progress Bar */}
      <div className="px-8 py-4 border-b border-slate-800">
        <div className="flex items-center gap-1">
          {STEPS.map((s, i) => (
            <div key={s} className="flex items-center flex-1">
              <div className={clsx(
                'flex items-center gap-2 text-xs font-medium',
                i < stepIdx ? 'text-emerald-400' : i === stepIdx ? 'text-indigo-400' : 'text-slate-600'
              )}>
                <div className={clsx(
                  'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0',
                  i < stepIdx ? 'bg-emerald-500 text-white' :
                  i === stepIdx ? 'bg-indigo-600 text-white' :
                  'bg-slate-800 text-slate-500'
                )}>
                  {i < stepIdx ? '✓' : i + 1}
                </div>
                <span className="hidden lg:block">{STEP_LABELS[s]}</span>
              </div>
              {i < STEPS.length - 1 && (
                <div className={clsx('flex-1 h-px mx-2', i < stepIdx ? 'bg-emerald-500' : 'bg-slate-800')} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="flex-1 flex items-start justify-center px-8 py-8">
        <div className="w-full max-w-2xl">
          {error && (
            <div className="mb-4 p-3 bg-red-900/30 border border-red-800 rounded-lg flex items-center gap-2 text-red-300 text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          {/* STEP: Business Type */}
          {step === 'business_type' && (
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-bold text-white mb-1">What type of business do you own?</h2>
                <p className="text-slate-400 text-sm">This helps us tailor your application.</p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {BUSINESS_TYPES.map(bt => (
                  <button
                    key={bt.value}
                    onClick={() => set('business_type', bt.value)}
                    className={clsx(
                      'p-4 rounded-xl border text-left transition-all',
                      form.business_type === bt.value
                        ? 'border-indigo-500 bg-indigo-600/20'
                        : 'border-slate-700 bg-slate-900 hover:border-slate-600'
                    )}
                  >
                    <div className="font-semibold text-white text-sm">{bt.label}</div>
                    <div className="text-slate-400 text-xs mt-1">{bt.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* STEP: Personal Info */}
          {step === 'personal' && (
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-bold text-white mb-1">Personal Information</h2>
                <p className="text-slate-400 text-sm">Tell us about yourself as the business owner.</p>
              </div>
              <div className="card space-y-4">
                <Field label="Full Legal Name" name="applicant_name" placeholder="Jane Smith" required />
                <Field label="Email Address" name="applicant_email" type="email" placeholder="jane@business.com" required />
                <Field label="Phone Number" name="applicant_phone" placeholder="(555) 000-0000" />
              </div>
            </div>
          )}

          {/* STEP: Business Details */}
          {step === 'business' && (
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-bold text-white mb-1">Business Details</h2>
                <p className="text-slate-400 text-sm">Tell us about your business.</p>
              </div>
              <div className="card space-y-4">
                <Field label="Business Name" name="business_name" placeholder="Acme Corp LLC" required />
                {!isSoleProprietor && (
                  <Field label="EIN (Employer Identification Number)" name="ein" placeholder="12-3456789" />
                )}
                <Field label="Years in Business" name="years_in_business" type="number" placeholder="3" required />
                <Field label="Industry" name="industry" required>
                  <select className="input" value={form.industry} onChange={e => set('industry', e.target.value)}>
                    <option value="">Select industry…</option>
                    {INDUSTRIES.map(i => <option key={i} value={i}>{i}</option>)}
                  </select>
                </Field>
                <Field label="State of Operation" name="state" required>
                  <select className="input" value={form.state} onChange={e => set('state', e.target.value)}>
                    <option value="">Select state…</option>
                    {US_STATES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </Field>
              </div>
            </div>
          )}

          {/* STEP: Financials */}
          {step === 'financials' && (
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-bold text-white mb-1">Financial Information</h2>
                <p className="text-slate-400 text-sm">Help us understand your financial health.</p>
              </div>
              <div className="card space-y-4">
                <Field label="Annual Business Revenue ($)" name="annual_revenue" type="number" placeholder="250000" required />
                <Field label="Monthly Operating Expenses ($)" name="monthly_expenses" type="number" placeholder="8000" required />
                <Field label="Personal Credit Score" name="credit_score" type="number" placeholder="680" required>
                  <input
                    type="number" className="input"
                    placeholder="680 (300–850)"
                    min="300" max="850"
                    value={form.credit_score}
                    onChange={e => set('credit_score', e.target.value)}
                  />
                </Field>
                <Field label="Existing Business Debt ($)" name="existing_debt" type="number" placeholder="0" />
              </div>
            </div>
          )}

          {/* STEP: Loan Request */}
          {step === 'loan' && (
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-bold text-white mb-1">Loan Request</h2>
                <p className="text-slate-400 text-sm">How much do you need and why?</p>
              </div>
              <div className="card space-y-4">
                <Field label="Requested Loan Amount ($)" name="loan_amount" type="number" placeholder="50000" required />
                <Field label="Purpose of Loan" name="loan_purpose" required>
                  <select className="input" value={form.loan_purpose} onChange={e => set('loan_purpose', e.target.value)}>
                    <option value="">Select purpose…</option>
                    {LOAN_PURPOSES.map(p => <option key={p} value={p}>{p}</option>)}
                  </select>
                </Field>
              </div>
            </div>
          )}

          {/* STEP: Bank Connect */}
          {step === 'bank' && (
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-bold text-white mb-1">Connect Your Bank</h2>
                <p className="text-slate-400 text-sm">
                  Securely share 12 months of transaction history. This significantly improves your approval odds — especially for "thin-file" businesses.
                </p>
              </div>
              <div className="card flex flex-col items-center text-center py-8 gap-4">
                {bankConnected ? (
                  <>
                    <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center">
                      <CheckCircle className="w-8 h-8 text-emerald-400" />
                    </div>
                    <div>
                      <div className="text-lg font-semibold text-emerald-400">Bank Account Connected!</div>
                      <div className="text-sm text-slate-400 mt-1">12 months of transaction data securely synced.</div>
                    </div>
                  </>
                ) : bankConnecting ? (
                  <>
                    <div className="w-16 h-16 bg-indigo-500/20 rounded-full flex items-center justify-center animate-pulse">
                      <Wifi className="w-8 h-8 text-indigo-400" />
                    </div>
                    <div>
                      <div className="text-lg font-semibold text-white">Connecting to your bank…</div>
                      <div className="text-sm text-slate-400 mt-1">Analyzing cash flow. Please wait.</div>
                    </div>
                    <div className="w-full max-w-xs space-y-2 text-left">
                      {['Authenticating securely…', 'Fetching 12 months of transactions…', 'Analyzing cash flow patterns…'].map((msg, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm text-slate-400">
                          <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-ping" style={{ animationDelay: `${i * 0.3}s` }} />
                          {msg}
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <>
                    <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center">
                      <Building2 className="w-8 h-8 text-slate-400" />
                    </div>
                    <div>
                      <div className="text-lg font-semibold text-white">Connect via Plaid</div>
                      <div className="text-sm text-slate-400 mt-1 max-w-sm">
                        We use bank-grade encryption. Your credentials are never stored on our servers.
                      </div>
                    </div>
                    <button onClick={connectBank} className="btn-primary px-8">
                      Connect My Bank Account
                    </button>
                    <button onClick={() => next()} className="text-sm text-slate-500 hover:text-slate-400 underline">
                      Skip for now (may affect decision)
                    </button>
                  </>
                )}
              </div>
            </div>
          )}

          {/* STEP: Review */}
          {step === 'review' && (
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-bold text-white mb-1">Review Your Application</h2>
                <p className="text-slate-400 text-sm">Please review all information before submitting.</p>
              </div>
              <div className="card space-y-3 text-sm">
                {[
                  ['Applicant', form.applicant_name],
                  ['Email', form.applicant_email],
                  ['Business', form.business_name],
                  ['Business Type', form.business_type],
                  ['Industry', form.industry],
                  ['Years in Business', form.years_in_business],
                  ['Annual Revenue', form.annual_revenue ? `$${parseInt(form.annual_revenue).toLocaleString()}` : '—'],
                  ['Monthly Expenses', form.monthly_expenses ? `$${parseInt(form.monthly_expenses).toLocaleString()}` : '—'],
                  ['Credit Score', form.credit_score],
                  ['Loan Amount', form.loan_amount ? `$${parseInt(form.loan_amount).toLocaleString()}` : '—'],
                  ['Loan Purpose', form.loan_purpose],
                  ['Bank Connected', bankConnected ? 'Yes ✓' : 'No'],
                ].map(([label, val]) => (
                  <div key={label} className="flex justify-between items-center py-1 border-b border-slate-800 last:border-0">
                    <span className="text-slate-400">{label}</span>
                    <span className="text-slate-100 font-medium">{val || '—'}</span>
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-500 text-center">
                By submitting, you authorize LoanMatrix AI to perform a soft credit inquiry and verify your business information.
              </p>
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between items-center mt-6">
            <button
              onClick={back}
              disabled={stepIdx === 0}
              className={clsx('flex items-center gap-2 btn-secondary', stepIdx === 0 && 'opacity-0 pointer-events-none')}
            >
              <ChevronLeft className="w-4 h-4" /> Back
            </button>

            {step === 'review' ? (
              <button onClick={submit} disabled={submitting} className="btn-primary px-8 flex items-center gap-2">
                {submitting ? 'Submitting…' : 'Submit Application'}
              </button>
            ) : step === 'bank' && bankConnected ? (
              <button onClick={next} className="btn-primary flex items-center gap-2">
                Continue <ChevronRight className="w-4 h-4" />
              </button>
            ) : step !== 'bank' ? (
              <button onClick={next} className="btn-primary flex items-center gap-2">
                Continue <ChevronRight className="w-4 h-4" />
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}
