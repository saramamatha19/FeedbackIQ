import { SENTIMENT_COLORS } from '@/lib/constants'

export function SentimentPill({ sentiment }: { sentiment: string }) {
  const color = SENTIMENT_COLORS[sentiment] ?? 'var(--color-neutral)'
  return (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium">
      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
      {sentiment}
    </span>
  )
}
