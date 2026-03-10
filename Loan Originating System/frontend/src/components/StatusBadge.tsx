import { ApplicationStatus } from '../types'

const STATUS_MAP: Record<string, { label: string; cls: string }> = {
  draft:          { label: 'Draft',          cls: 'badge-draft' },
  submitted:      { label: 'Processing',     cls: 'badge-referred' },
  auto_approved:  { label: 'Approved',       cls: 'badge-approved' },
  auto_declined:  { label: 'Declined',       cls: 'badge-declined' },
  referred:       { label: 'Under Review',   cls: 'badge-referred' },
  fraud_hold:     { label: 'Fraud Hold',     cls: 'badge-fraud' },
  funded:         { label: 'Funded',         cls: 'badge-approved' },
}

export default function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_MAP[status] ?? { label: status, cls: 'badge-draft' }
  return <span className={cfg.cls}>{cfg.label}</span>
}
