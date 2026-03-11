interface ScoreGaugeProps {
  score: number
  size?: 'sm' | 'lg'
}

export default function ScoreGauge({ score, size = 'lg' }: ScoreGaugeProps) {
  const pct = (score / 1000) * 100
  const radius = size === 'lg' ? 54 : 36
  const stroke = size === 'lg' ? 10 : 7
  const cx = radius + stroke
  const cy = radius + stroke
  const circumference = 2 * Math.PI * radius
  const dash = (pct / 100) * circumference

  const color =
    score >= 700 ? '#10b981' :
    score >= 400 ? '#f59e0b' :
    '#ef4444'

  const label =
    score >= 700 ? 'Prime' :
    score >= 400 ? 'Near-Prime' :
    'Subprime'

  const svgSize = (radius + stroke) * 2

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative" style={{ width: svgSize, height: svgSize }}>
        <svg width={svgSize} height={svgSize}>
          {/* Track */}
          <circle
            cx={cx} cy={cy} r={radius}
            fill="none"
            stroke="#1e293b"
            strokeWidth={stroke}
          />
          {/* Progress */}
          <circle
            cx={cx} cy={cy} r={radius}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeDasharray={circumference}
            strokeDashoffset={circumference - dash}
            strokeLinecap="round"
            transform={`rotate(-90 ${cx} ${cy})`}
            style={{ transition: 'stroke-dashoffset 0.8s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`font-bold ${size === 'lg' ? 'text-2xl' : 'text-lg'}`} style={{ color }}>
            {score}
          </span>
          {size === 'lg' && (
            <span className="text-xs text-slate-500">/1000</span>
          )}
        </div>
      </div>
      <span className={`text-xs font-semibold`} style={{ color }}>
        {label}
      </span>
    </div>
  )
}
