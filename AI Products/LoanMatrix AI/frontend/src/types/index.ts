export interface Application {
  id: number
  session_id: string
  applicant_name: string | null
  applicant_email: string | null
  applicant_phone: string | null
  business_name: string | null
  business_type: string | null
  ein: string | null
  years_in_business: number | null
  industry: string | null
  state: string | null
  annual_revenue: number | null
  monthly_expenses: number | null
  credit_score: number | null
  existing_debt: number | null
  loan_amount: number | null
  loan_purpose: string | null
  bank_connected: boolean
  avg_bank_balance: number | null
  nsf_count: number
  monthly_deposits_avg: number | null
  health_score: number | null
  status: ApplicationStatus
  created_at: string
  updated_at: string
}

export type ApplicationStatus =
  | 'draft'
  | 'submitted'
  | 'auto_approved'
  | 'auto_declined'
  | 'referred'
  | 'fraud_hold'
  | 'funded'

export interface Document {
  id: number
  application_id: number
  doc_type: string
  filename: string
  file_size: number
  tamper_score: number
  extracted_data: Record<string, any> | null
  status: string
  uploaded_at: string
}

export interface Decision {
  id: number
  application_id: number
  decision_type: string
  reasons: string[] | null
  shap_values: Record<string, number> | null
  adverse_action_codes: string[] | null
  notes: string | null
  decided_by: string
  final_rate: number | null
  final_amount: number | null
  final_term_months: number | null
  decided_at: string
}

export interface Offer {
  id: number
  application_id: number
  product_type: string
  rate: number
  term_months: number
  amount: number
  monthly_payment: number
  created_at: string
}

export interface RiskAlert {
  severity: 'high' | 'medium' | 'low'
  code: string
  message: string
}

export interface ThresholdConfig {
  id: number
  auto_approve_min: number
  auto_decline_max: number
  max_loan_amount: number
  min_years_in_business: number
  updated_by: string
  updated_at: string
  pending_approve_min: number | null
  pending_decline_max: number | null
  pending_requested_by: string | null
  pending_approved_by: string | null
}

export interface ComplianceMetrics {
  total_applications: number
  auto_approved: number
  auto_declined: number
  referred: number
  fraud_hold: number
  approval_rate: number
  avg_health_score: number
  by_business_type: Record<string, { total: number; approved: number; rate: number }>
  by_industry: Record<string, { total: number; approved: number; rate: number }>
  score_distribution: { range: string; count: number }[]
}
