/**
 * S-09 Profile — user account settings, password change, notification preferences.
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { authApi, notificationsApi } from '../../services/api'
import { useAuthStore } from '../../store/authStore'
import toast from 'react-hot-toast'

const NOTIFICATION_LABELS: Record<string, string> = {
  pipeline_completed:         'Pipeline completed',
  pipeline_failed:            'Pipeline failed',
  agent_failed:               'Section agent failed',
  compliance_review_required: 'Compliance review required',
  section_edit_saved:         'Manual edit saved',
  section_rerun_completed:    'Section re-run completed',
}

export default function ProfilePage() {
  const { user, setUser } = useAuthStore()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [form, setForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })

  const changePw = useMutation({
    mutationFn: () => authApi.changePassword({
      current_password: form.current_password,
      new_password: form.new_password,
    }),
    onSuccess: () => {
      toast.success('Password updated')
      setForm({ current_password: '', new_password: '', confirm_password: '' })
      // Re-fetch user so force_password_change is cleared in the store
      authApi.me().then((res) => {
        setUser(res.data)
        if (res.data.force_password_change === false && user?.force_password_change) {
          navigate('/dashboard')
        }
      }).catch(() => {})
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail ?? 'Password change failed'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (form.new_password !== form.confirm_password) {
      toast.error('Passwords do not match')
      return
    }
    if (form.new_password.length < 12) {
      toast.error('Password must be at least 12 characters')
      return
    }
    changePw.mutate()
  }

  // Notification preferences
  const { data: prefs = [] } = useQuery({
    queryKey: ['notification-prefs'],
    queryFn: () => notificationsApi.getPreferences().then((r) => r.data),
  })

  const updatePref = useMutation({
    mutationFn: ({ event_type, is_enabled }: { event_type: string; is_enabled: boolean }) =>
      notificationsApi.updatePreference(event_type, is_enabled),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notification-prefs'] }),
    onError: () => toast.error('Failed to update preference'),
  })

  const isPrefEnabled = (eventType: string): boolean => {
    const found = prefs.find((p) => p.event_type === eventType)
    return found ? found.is_enabled : true  // default enabled if not yet set
  }

  const ROLE_LABELS: Record<string, string> = {
    admin: 'Administrator — full access',
    reviewer: 'Reviewer — can review and sign compliance reports',
    user: 'Medical Writer — can create and edit CSR runs',
  }

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>

      {user?.force_password_change && (
        <div className="bg-amber-50 border border-amber-300 rounded-lg px-4 py-3 text-sm text-amber-800">
          <strong>Action required:</strong> You must change your password before continuing.
          This is a temporary password assigned by your administrator.
        </div>
      )}

      {/* User info card */}
      <div className="card p-6">
        <div className="flex items-center gap-4 mb-5">
          <div className="w-14 h-14 rounded-full bg-brand-600 text-white flex items-center justify-center text-2xl font-bold">
            {user?.full_name?.[0]?.toUpperCase() ?? user?.username?.[0]?.toUpperCase() ?? 'U'}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-800">{user?.full_name || user?.username}</h2>
            <p className="text-sm text-gray-500">{user?.email}</p>
            <span className="badge-blue capitalize mt-1 inline-block">{user?.role}</span>
          </div>
        </div>

        <div className="border-t border-gray-100 pt-4 space-y-2">
          {[
            { label: 'Username', value: user?.username },
            { label: 'Full Name', value: user?.full_name },
            { label: 'Email', value: user?.email },
            { label: 'Role', value: ROLE_LABELS[user?.role ?? ''] ?? user?.role },
          ].map(({ label, value }) => (
            <div key={label} className="flex items-center gap-4 py-1">
              <span className="w-24 text-xs font-medium text-gray-500">{label}</span>
              <span className="text-sm text-gray-800">{value ?? '—'}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Change password */}
      <div className="card p-6">
        <h2 className="font-semibold text-gray-800 mb-4">Change Password</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {[
            { label: 'Current Password', key: 'current_password' },
            { label: 'New Password',     key: 'new_password' },
            { label: 'Confirm New Password', key: 'confirm_password' },
          ].map(({ label, key }) => (
            <div key={key}>
              <label className="label">{label}</label>
              <input
                type="password"
                className="input"
                value={(form as any)[key]}
                onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                placeholder="••••••••"
              />
            </div>
          ))}
          <button
            type="submit"
            className="btn-primary"
            disabled={changePw.isPending || !form.current_password || !form.new_password}
          >
            {changePw.isPending ? 'Updating...' : 'Update Password'}
          </button>
        </form>

        <div className="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-500 space-y-1">
          <p>Password requirements:</p>
          <ul className="list-disc pl-4 space-y-0.5">
            <li>Minimum 12 characters</li>
            <li>At least one uppercase letter</li>
            <li>At least one lowercase letter</li>
            <li>At least one digit</li>
            <li>At least one special character (!@#$%^&amp;* etc.)</li>
          </ul>
        </div>
      </div>

      {/* Notification preferences */}
      <div className="card p-6">
        <h2 className="font-semibold text-gray-800 mb-1">Notification Preferences</h2>
        <p className="text-xs text-gray-500 mb-4">
          Choose which events trigger in-app notifications for your runs.
        </p>
        <div className="space-y-3">
          {Object.entries(NOTIFICATION_LABELS).map(([eventType, label]) => {
            const enabled = isPrefEnabled(eventType)
            return (
              <div key={eventType} className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{label}</span>
                <button
                  onClick={() => updatePref.mutate({ event_type: eventType, is_enabled: !enabled })}
                  disabled={updatePref.isPending}
                  className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none ${
                    enabled ? 'bg-brand-600' : 'bg-gray-300'
                  }`}
                  role="switch"
                  aria-checked={enabled}
                >
                  <span
                    className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${
                      enabled ? 'translate-x-4' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
