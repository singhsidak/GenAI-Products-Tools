import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../../services/api'
import { useAuthStore } from '../../store/authStore'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [loading, setLoading] = useState(false)
  const { setUser } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.username || !form.password) return

    setLoading(true)
    try {
      const res = await authApi.login(form)
      setUser(res.data.user)
      navigate('/dashboard')
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? 'Login failed'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-900 to-brand-700 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🧬</div>
          <h1 className="text-2xl font-bold text-white">CSR-Gen</h1>
          <p className="text-brand-100 text-sm mt-1 opacity-80">Clinical Study Report Generator</p>
        </div>

        {/* Card */}
        <div className="card p-8">
          <h2 className="text-lg font-semibold text-gray-800 mb-6">Sign in to your account</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Username</label>
              <input
                type="text"
                className="input"
                placeholder="Enter username"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                autoFocus
                autoComplete="username"
              />
            </div>

            <div>
              <label className="label">Password</label>
              <input
                type="password"
                className="input"
                placeholder="Enter password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                autoComplete="current-password"
              />
            </div>

            <button
              type="submit"
              className="btn-primary w-full mt-2"
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <p className="text-xs text-gray-400 text-center mt-6">
            Contact your administrator if you need access.
          </p>
        </div>

        <p className="text-center text-brand-200 text-xs mt-4 opacity-60">
          ICH E3 compliant · Powered by Gemini 3 Flash
        </p>
      </div>
    </div>
  )
}
