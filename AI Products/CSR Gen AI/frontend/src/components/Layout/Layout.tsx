/**
 * Main app layout: sidebar navigation + top bar + content area.
 */
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { authApi } from '../../services/api'
import { useNotifications } from '../../hooks/useNotifications'
import NotificationBell from '../Notifications/NotificationBell'
import toast from 'react-hot-toast'

interface NavItem {
  to: string
  label: string
  icon: string
  roles?: string[]
}

const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/upload', label: 'New Run', icon: '⬆️' },
  { to: '/runs', label: 'All Runs', icon: '📋' },
  { to: '/admin', label: 'Admin', icon: '⚙️', roles: ['admin'] },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const { unreadCount } = useNotifications()

  const handleLogout = async () => {
    try {
      await authApi.logout()
    } catch {
      // ignore errors
    }
    logout()
    navigate('/login')
  }

  const visibleItems = NAV_ITEMS.filter(
    (item) => !item.roles || (user && item.roles.includes(user.role)),
  )

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <aside className="w-56 flex-shrink-0 bg-brand-900 flex flex-col">
        {/* Logo */}
        <div className="px-5 py-4 border-b border-brand-700">
          <Link to="/dashboard" className="flex items-center gap-2">
            <span className="text-2xl">🧬</span>
            <span className="text-white font-bold text-lg leading-tight">CSR-Gen</span>
          </Link>
          <p className="text-brand-100 text-xs mt-0.5 opacity-70">Clinical Study Reports</p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {visibleItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive
                  ? 'bg-brand-600 text-white'
                  : 'text-brand-100 hover:bg-brand-700 hover:text-white'
                }`
              }
            >
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* User info */}
        <div className="px-4 py-4 border-t border-brand-700">
          <Link
            to="/profile"
            className="flex items-center gap-3 text-brand-100 hover:text-white transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
              {user?.full_name?.[0]?.toUpperCase() ?? user?.username?.[0]?.toUpperCase() ?? 'U'}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium truncate">{user?.full_name || user?.username}</p>
              <p className="text-xs opacity-60 capitalize">{user?.role}</p>
            </div>
          </Link>
          <button
            onClick={handleLogout}
            className="mt-3 w-full text-left text-xs text-brand-200 hover:text-white transition-colors px-1"
          >
            Sign out →
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar */}
        <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6 flex-shrink-0">
          <div />
          <div className="flex items-center gap-4">
            <NotificationBell unreadCount={unreadCount} />
            <span className="text-sm text-gray-500">{user?.email}</span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
