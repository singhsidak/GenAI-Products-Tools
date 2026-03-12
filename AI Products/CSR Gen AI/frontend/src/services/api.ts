/**
 * Axios API client — all backend endpoint wrappers.
 * Authentication via HTTP-only cookie (set by /api/auth/login).
 */
import axios, { AxiosError } from 'axios'

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

export const api = axios.create({
  baseURL: '/api',
  withCredentials: true,   // send the auth cookie
  headers: { 'Content-Type': 'application/json' },
})

// Global 401 interceptor — redirect to login
api.interceptors.response.use(
  (res) => res,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

// ---------------------------------------------------------------------------
// Types (mirrors backend Pydantic schemas)
// ---------------------------------------------------------------------------

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: 'admin' | 'reviewer' | 'user'
  is_active: boolean
  force_password_change: boolean
  created_at: string
}

export interface LoginRequest { username: string; password: string }
export interface LoginResponse { message: string; user: User }

export interface RunListItem {
  id: number
  run_id: string
  run_name: string
  study_id: string
  status: string
  started_at: string | null
  completed_at: string | null
  created_at: string
  duration_minutes: number | null
  initiated_by_username: string
  total_cost_usd?: number
  total_tokens?: number
  // Optional — only present in single-run GET response
  completed_sections?: number
  failed_sections?: number
  total_sections?: number
  total_tokens_used?: number
}

export interface RunDetail {
  id: number
  run_id: string
  study_id: string
  run_name: string
  status: string
  current_phase: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
  initiated_by: number
  total_input_tokens?: number   // admin-only
  total_output_tokens?: number  // admin-only
  total_cost_usd?: number       // admin-only
  error_message: string | null
  parent_run_id: string | null
  completed_sections: number
  failed_sections: number
  total_sections: number
  total_tokens_used: number
}

export interface RunDocument {
  id: number
  zone: string
  original_filename: string
  stored_path: string
  file_size_bytes: number | null
  upload_status: string
  created_at: string
}

export interface SectionSummary {
  id: number
  run_id: string
  section_number: number
  section_name: string
  title: string             // alias for section_name
  agent_name: string
  status: string
  word_count: number | null
  is_human_edited: boolean
  is_edited: boolean        // alias for is_human_edited
  retry_count: number
  started_at: string | null
  completed_at: string | null
  edited_at: string | null
}

export interface SectionDetail extends SectionSummary {
  content: string | null
  compliance_trace: ComplianceTraceItem[] | null
  data_not_available_count: number
  gcp_deviation_count: number
  // Not in backend response — optional for backwards compat
  tokens_used?: number | null
  generation_cost_usd?: number | null
  edit_count?: number
}

export interface ComplianceTraceItem {
  rule_id: string
  rule_description: string
  status: 'pass' | 'fail' | 'warning'
  details?: string
}

export interface ComplianceReport {
  id: number
  run_id: string
  version_id: string
  overall_status: string
  data_not_available_count: number
  gcp_deviation_count: number
  report_content: Record<string, unknown>
  is_signed: boolean
  signed_by_username: string | null
  signed_at: string | null
  created_at: string
}

export interface ComplianceAuditEntry {
  id: number
  user_id: number
  username: string
  action: string
  timestamp: string
}

export interface AgentLog {
  id: number
  agent_name: string
  phase: string | null
  status: string
  message: string | null
  timestamp: string
  input_tokens?: number
  output_tokens?: number
  estimated_cost_usd?: number
}

export interface Notification {
  id: number
  run_id: string | null
  event_type: string
  message: string
  is_read: boolean
  created_at: string
}

export interface AnalyticsSummary {
  period: string
  total_runs: number
  completed_runs: number
  failed_runs: number
  total_cost_usd: number
  avg_cost_per_run_usd: number
  total_tokens: number
  total_tokens_used: number
  runs_by_status: Record<string, number>
  avg_completion_minutes: number | null
  compliance_pass_rate: number | null
}

export interface OutputFile {
  id: number
  run_id: string
  file_type: string
  stored_path: string
  file_size_bytes: number | null
  created_at: string
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export const authApi = {
  login: (data: LoginRequest) =>
    api.post<LoginResponse>('/auth/login', data),

  logout: () =>
    api.post('/auth/logout'),

  me: () =>
    api.get<User>('/auth/me'),

  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
}

// ---------------------------------------------------------------------------
// Runs
// ---------------------------------------------------------------------------

export const runsApi = {
  list: (params?: { limit?: number; offset?: number; status?: string }) =>
    api.get<RunListItem[]>('/runs', { params }),

  get: (runId: number) =>
    api.get<RunDetail>(`/runs/${runId}`),

  create: (formData: FormData) =>
    api.post<RunDetail>('/runs', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  retrySection: (runId: number, sectionNumber: number) =>
    api.post(`/runs/${runId}/retry/${sectionNumber}`),

  rerun: (runId: number, data: { scope?: string; section_number?: number; replace_documents?: boolean }) =>
    api.post(`/runs/${runId}/rerun`, data),

  getLogs: (runId: number) =>
    api.get<AgentLog[]>(`/runs/${runId}/logs`),

  download: (runId: number, fileType: 'pdf' | 'docx' | 'index_csv') =>
    api.get(`/runs/${runId}/download/${fileType}`, { responseType: 'blob' }),
}

// ---------------------------------------------------------------------------
// Sections
// ---------------------------------------------------------------------------

export const sectionsApi = {
  list: (runId: number) =>
    api.get<SectionSummary[]>(`/runs/${runId}/sections`),

  get: (runId: number, sectionNumber: number) =>
    api.get<SectionDetail>(`/runs/${runId}/sections/${sectionNumber}`),

  update: (runId: number, sectionNumber: number, data: { content: string }) =>
    api.put<SectionDetail>(`/runs/${runId}/sections/${sectionNumber}`, data),

  rerun: (runId: number, sectionNumber: number) =>
    api.post(`/runs/${runId}/sections/${sectionNumber}/rerun`),
}

// ---------------------------------------------------------------------------
// Compliance
// ---------------------------------------------------------------------------

export const complianceApi = {
  get: (runId: number) =>
    api.get<ComplianceReport>(`/runs/${runId}/compliance`),

  sign: (runId: number, data: { acknowledged: boolean }) =>
    api.post(`/runs/${runId}/compliance/sign`, data),

  getAudit: (runId: number) =>
    api.get<ComplianceAuditEntry[]>(`/runs/${runId}/compliance/audit`),
}

// ---------------------------------------------------------------------------
// Users (Admin)
// ---------------------------------------------------------------------------

export const usersApi = {
  list: () =>
    api.get<User[]>('/admin/users'),

  create: (data: {
    username: string; email: string; temp_password: string
    role: string; full_name: string
  }) =>
    api.post<{ detail: string; user_id: number; username: string }>('/admin/users', data),

  update: (userId: number, data: { is_active?: boolean; role?: string; full_name?: string }) =>
    api.put<User>(`/admin/users/${userId}`, data),

  resetPassword: (userId: number) =>
    api.post<{ temp_password: string; username: string; detail: string }>(`/admin/users/${userId}/reset-password`),
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export const dashboardApi = {
  getAnalytics: () =>
    api.get<AnalyticsSummary>('/dashboard/analytics'),
}

// ---------------------------------------------------------------------------
// Notifications
// ---------------------------------------------------------------------------

export interface NotificationPreference {
  event_type: string
  is_enabled: boolean
}

export const notificationsApi = {
  list: (params?: { unread_only?: boolean }) =>
    api.get<Notification[]>('/dashboard/notifications', { params }),

  markRead: (notificationId: number) =>
    api.post(`/dashboard/notifications/${notificationId}/read`),

  markAllRead: () =>
    api.post('/dashboard/notifications/read-all'),

  getPreferences: () =>
    api.get<NotificationPreference[]>('/dashboard/notifications/preferences'),

  updatePreference: (event_type: string, is_enabled: boolean) =>
    api.put('/dashboard/notifications/preferences', { event_type, is_enabled }),
}
