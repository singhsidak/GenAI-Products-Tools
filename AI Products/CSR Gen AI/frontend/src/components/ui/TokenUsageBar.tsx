/**
 * Displays cumulative token usage and estimated cost for a run.
 */
interface Props {
  tokensUsed: number
  costUsd: number
}

// Rough cost reference for UI display (Gemini 3 Flash Preview pricing placeholder)
const COST_PER_1K_TOKENS = 0.000375

export default function TokenUsageBar({ tokensUsed, costUsd }: Props) {
  if (!tokensUsed) return null

  return (
    <div className="flex items-center gap-6 px-4 py-2 bg-gray-50 rounded-lg border border-gray-200 text-sm">
      <div>
        <span className="text-gray-500 mr-1">Tokens:</span>
        <span className="font-semibold text-gray-800">{tokensUsed.toLocaleString()}</span>
      </div>
      <div>
        <span className="text-gray-500 mr-1">Est. Cost:</span>
        <span className="font-semibold text-gray-800">
          ${costUsd > 0 ? costUsd.toFixed(4) : (tokensUsed / 1000 * COST_PER_1K_TOKENS).toFixed(4)}
        </span>
      </div>
    </div>
  )
}
