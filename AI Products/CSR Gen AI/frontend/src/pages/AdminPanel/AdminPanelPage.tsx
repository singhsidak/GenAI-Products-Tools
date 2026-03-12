/**
 * S-08 Admin Panel — user management (Admin only).
 */
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi, type User } from '../../services/api'
import StatusBadge from '../../components/ui/StatusBadge'
import toast from 'react-hot-toast'

const ROLES = ['user', 'reviewer', 'admin'] as const

function CreateUserModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    username: '', email: '', temp_password: '', role: 'user', full_name: '',
  })

  const createMutation = useMutation({
    mutationFn: () => usersApi.create(form),
    onSuccess: () => {
      toast.success(`User '${form.username}' created`)
      qc.invalidateQueries({ queryKey: ['users'] })
      onClose()
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail ?? 'Create failed'),
  })

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
      <div className="card p-6 w-full max-w-md">
        <h2 className="font-semibold text-gray-800 mb-4">Create New User</h2>
        <div className="space-y-3">
          {[
            { label: 'Full Name', key: 'full_name', type: 'text', placeholder: 'Dr. Jane Smith' },
            { label: 'Username', key: 'username',  type: 'text', placeholder: 'jsmith' },
            { label: 'Email',    key: 'email',     type: 'email', placeholder: 'jane@example.com' },
            { label: 'Password', key: 'temp_password',  type: 'password', placeholder: 'Temporary password (12+ chars)' },
          ].map(({ label, key, type, placeholder }) => (
            <div key={key}>
              <label className="label">{label}</label>
              <input
                type={type}
                className="input"
                placeholder={placeholder}
                value={(form as any)[key]}
                onChange={(e) => setForm({ ...form, [key]: e.target.value })}
              />
            </div>
          ))}
          <div>
            <label className="label">Role</label>
            <select
              className="input"
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex gap-3 mt-5">
          <button
            onClick={() => createMutation.mutate()}
            className="btn-primary flex-1"
            disabled={createMutation.isPending || !form.username || !form.temp_password || !form.email}
          >
            {createMutation.isPending ? 'Creating...' : 'Create User'}
          </button>
          <button onClick={onClose} className="btn-ghost">Cancel</button>
        </div>
      </div>
    </div>
  )
}

export default function AdminPanelPage() {
  const qc = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)

  const { data: users = [], isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersApi.list().then((r) => r.data),
  })

  const updateMutation = useMutation({
    mutationFn: ({ userId, data }: { userId: number; data: Partial<User> }) =>
      usersApi.update(userId, data),
    onSuccess: () => {
      toast.success('User updated')
      qc.invalidateQueries({ queryKey: ['users'] })
    },
    onError: () => toast.error('Update failed'),
  })

  const resetPassword = useMutation({
    mutationFn: (userId: number) => usersApi.resetPassword(userId),
    onSuccess: (res) => {
      toast.success(
        `Temporary password: ${res.data.temp_password}`,
        { duration: 10_000 }
      )
    },
    onError: () => toast.error('Reset failed'),
  })

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-sm text-gray-500 mt-1">Manage team members and their access roles.</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary">
          + New User
        </button>
      </div>

      {/* Users table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {['User', 'Role', 'Status', 'Actions'].map((h) => (
                  <th key={h} className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {isLoading ? (
                <tr><td colSpan={4} className="px-5 py-8 text-center text-gray-400">Loading...</td></tr>
              ) : users.map((u: User) => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-sm font-bold">
                        {u.full_name?.[0]?.toUpperCase() ?? u.username[0].toUpperCase()}
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">{u.full_name || u.username}</p>
                        <p className="text-xs text-gray-400">@{u.username} · {u.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <select
                      className="text-sm border border-gray-200 rounded-lg px-2 py-1 focus:outline-none focus:ring-1 focus:ring-brand-500"
                      value={u.role}
                      onChange={(e) => updateMutation.mutate({ userId: u.id, data: { role: e.target.value } })}
                    >
                      {ROLES.map((r) => (
                        <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
                      ))}
                    </select>
                  </td>
                  <td className="px-5 py-4">
                    <button
                      onClick={() => updateMutation.mutate({ userId: u.id, data: { is_active: !u.is_active } })}
                      className={`badge cursor-pointer ${u.is_active ? 'badge-green' : 'badge-gray'}`}
                    >
                      {u.is_active ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td className="px-5 py-4">
                    <button
                      onClick={() => resetPassword.mutate(u.id)}
                      className="text-xs text-brand-600 hover:underline"
                      disabled={resetPassword.isPending}
                    >
                      Reset Password
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showCreate && <CreateUserModal onClose={() => setShowCreate(false)} />}
    </div>
  )
}
