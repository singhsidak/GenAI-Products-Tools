interface Props {
  value: number    // 0-100
  label?: string
  color?: string
  showPercent?: boolean
}

export default function ProgressBar({ value, label, color = 'bg-brand-500', showPercent = true }: Props) {
  const pct = Math.min(100, Math.max(0, value))
  return (
    <div>
      {(label || showPercent) && (
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          {label && <span>{label}</span>}
          {showPercent && <span>{pct}%</span>}
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
