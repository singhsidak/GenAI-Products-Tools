/**
 * Pipeline run / section status badge.
 */

const STATUS_MAP: Record<string, { label: string; cls: string }> = {
  // Run statuses (backend: queued | in_progress | completed | failed | partial | awaiting_review)
  queued:              { label: 'Queued',          cls: 'badge-gray' },
  in_progress:         { label: 'In Progress',     cls: 'badge-blue' },
  awaiting_review:     { label: 'Awaiting Review', cls: 'badge-yellow' },
  completed:           { label: 'Completed',       cls: 'badge-green' },
  failed:              { label: 'Failed',          cls: 'badge-red' },
  partial:             { label: 'Partial',         cls: 'badge-yellow' },
  // Section statuses (backend: pending | in_progress | completed | failed | retried_completed | rerun_pending)
  pending:             { label: 'Pending',         cls: 'badge-gray' },
  retried_completed:   { label: 'Completed',       cls: 'badge-green' },
  rerun_pending:       { label: 'Rerunning',       cls: 'badge-blue' },
  // Compliance trace statuses
  pass:                { label: 'Pass',            cls: 'badge-green' },
  fail:                { label: 'Fail',            cls: 'badge-red' },
  warning:             { label: 'Warning',         cls: 'badge-yellow' },
}

interface Props {
  status: string
}

export default function StatusBadge({ status }: Props) {
  const { label, cls } = STATUS_MAP[status?.toLowerCase()] ?? {
    label: status,
    cls: 'badge-gray',
  }
  return <span className={cls}>{label}</span>
}
