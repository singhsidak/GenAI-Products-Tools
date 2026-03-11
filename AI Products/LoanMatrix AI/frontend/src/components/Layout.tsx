import { Outlet, NavLink, useLocation } from 'react-router-dom'
import {
  CreditCard, Users, Shield, Settings, LayoutDashboard,
  FileText, ChevronRight, Activity
} from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { to: '/apply', icon: CreditCard, label: 'Apply for Loan', group: 'Borrower' },
  { to: '/applications', icon: LayoutDashboard, label: 'All Applications', group: 'Borrower' },
  { to: '/underwriter', icon: Users, label: 'Underwriter Queue', group: 'Internal' },
  { to: '/compliance', icon: Shield, label: 'Compliance', group: 'Internal' },
  { to: '/admin', icon: Settings, label: 'Admin Settings', group: 'Internal' },
]

const groups = ['Borrower', 'Internal']

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col flex-shrink-0">
        {/* Logo */}
        <div className="px-6 py-5 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-bold text-white text-sm">LoanMatrix</div>
              <div className="text-indigo-400 text-xs font-medium">AI Platform</div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          {groups.map(group => (
            <div key={group}>
              <div className="px-3 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                {group}
              </div>
              <ul className="space-y-1">
                {navItems.filter(n => n.group === group).map(({ to, icon: Icon, label }) => (
                  <li key={to}>
                    <NavLink
                      to={to}
                      className={({ isActive }) =>
                        clsx(
                          'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                          isActive
                            ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                            : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800'
                        )
                      }
                    >
                      <Icon className="w-4 h-4 flex-shrink-0" />
                      {label}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
            <span className="text-xs text-slate-500">All systems operational</span>
          </div>
          <div className="text-xs text-slate-600 mt-1">v1.0.0 • SQLite Mode</div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto bg-slate-950">
        <Outlet />
      </main>
    </div>
  )
}
