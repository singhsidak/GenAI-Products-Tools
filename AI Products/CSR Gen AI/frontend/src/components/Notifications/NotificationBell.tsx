import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { notificationsApi, type Notification } from '../../services/api'
import { formatDistanceToNow } from 'date-fns'

interface Props {
  unreadCount: number
}

const EVENT_ICONS: Record<string, string> = {
  pipeline_completed:         '✅',
  pipeline_failed:            '❌',
  agent_failed:               '⚠️',
  compliance_review_required: '🔍',
  section_edit_saved:         '✏️',
  section_rerun_completed:    '🔄',
}

function notifIcon(eventType: string): string {
  return EVENT_ICONS[eventType] ?? '🔔'
}

function notifRunPath(n: Notification): string | null {
  if (!n.run_id) return null
  if (n.event_type === 'compliance_review_required') return `/runs/${n.run_id}/compliance`
  return `/runs/${n.run_id}`
}

export default function NotificationBell({ unreadCount }: Props) {
  const [open, setOpen] = useState(false)
  const qc = useQueryClient()
  const navigate = useNavigate()

  const { data: notifications = [] } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.list().then((r) => r.data),
    enabled: open,
  })

  const markAll = useMutation({
    mutationFn: () => notificationsApi.markAllRead(),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  })

  const markOne = useMutation({
    mutationFn: (id: number) => notificationsApi.markRead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  })

  const handleClick = (n: Notification) => {
    if (!n.is_read) markOne.mutate(n.id)
    const path = notifRunPath(n)
    if (path) {
      setOpen(false)
      navigate(path)
    }
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
        title="Notifications"
      >
        🔔
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center px-1">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />

          {/* Dropdown */}
          <div className="absolute right-0 top-11 w-80 bg-white rounded-xl shadow-lg border border-gray-200 z-50 overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
              <h3 className="font-semibold text-sm text-gray-800">Notifications</h3>
              {unreadCount > 0 && (
                <button
                  onClick={() => markAll.mutate()}
                  className="text-xs text-brand-600 hover:underline"
                >
                  Mark all read
                </button>
              )}
            </div>

            <div className="max-h-80 overflow-y-auto divide-y divide-gray-50">
              {notifications.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-8">No notifications</p>
              ) : (
                notifications.slice(0, 20).map((n: Notification) => (
                  <div
                    key={n.id}
                    onClick={() => handleClick(n)}
                    className={`px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors ${
                      !n.is_read ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-start gap-2 min-w-0">
                        <span className="flex-shrink-0 mt-0.5 text-sm">{notifIcon(n.event_type)}</span>
                        <p className={`text-sm font-medium ${!n.is_read ? 'text-gray-900' : 'text-gray-600'}`}>
                          {n.event_type.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                        </p>
                      </div>
                      {!n.is_read && (
                        <div className="w-2 h-2 rounded-full bg-brand-500 mt-1 flex-shrink-0" />
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5 line-clamp-2 ml-6">{n.message}</p>
                    <p className="text-xs text-gray-400 mt-1 ml-6">
                      {formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}
                    </p>
                  </div>
                ))
              )}
            </div>

            {notifications.length > 20 && (
              <div className="border-t border-gray-100 px-4 py-2 text-center">
                <span className="text-xs text-gray-400">
                  Showing 20 of {notifications.length} — older notifications visible in run history
                </span>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
