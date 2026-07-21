import { Badge } from '@/components/ui/Badge'
import type { Prediction } from '@/api/types'
import {
  BUSINESS_IMPACT_FILL,
  CATEGORY_COLORS,
  CATEGORY_ICONS,
  EMOTION_EMOJI,
  SENTIMENT_COLORS,
  URGENCY_STYLES,
} from '@/lib/constants'

function Meter({ label, fraction, color }: { label: string; fraction: number; color: string }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs text-[var(--color-ink-muted)]">
        <span>{label}</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-black/10 dark:bg-white/10">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${fraction * 100}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}

export function PredictionSummary({ prediction }: { prediction: Prediction }) {
  return (
    <div className="space-y-5">
      <div className="space-y-3 rounded-lg border border-[var(--color-border)] p-3">
        <div className="text-sm">
          <div className="mb-1 text-[var(--color-ink-muted)]">Category</div>
          <Badge color={CATEGORY_COLORS[prediction.category] ?? '#9ca3af'}>
            {CATEGORY_ICONS[prediction.category] ?? '📋'} {prediction.category}
          </Badge>
        </div>
        <div className="text-sm">
          <div className="mb-1 text-[var(--color-ink-muted)]">Sentiment</div>
          <Badge color={SENTIMENT_COLORS[prediction.sentiment]}>{prediction.sentiment}</Badge>
        </div>
        <div className="text-sm">
          <div className="mb-1 text-[var(--color-ink-muted)]">Emotion</div>
          <Badge color="#9ca3af">
            {EMOTION_EMOJI[prediction.emotion] ?? ''} {prediction.emotion}
          </Badge>
        </div>
        <div className="text-sm">
          <div className="mb-1 text-[var(--color-ink-muted)]">Urgency</div>
          <Badge color={URGENCY_STYLES[prediction.urgency]?.color ?? '#9ca3af'}>{prediction.urgency}</Badge>
        </div>
        <div className="text-sm">
          <div className="mb-1 text-[var(--color-ink-muted)]">Theme</div>
          <span className="font-medium">{prediction.theme}</span>
        </div>
      </div>

      <div className="space-y-3">
        <Meter
          label={`Business Impact — ${prediction.business_impact}`}
          fraction={BUSINESS_IMPACT_FILL[prediction.business_impact] ?? 0.1}
          color="var(--color-accent)"
        />
        <Meter
          label={`Confidence — ${prediction.confidence_score}%`}
          fraction={prediction.confidence_score / 100}
          color="var(--color-accent)"
        />
      </div>

      <div>
        <div className="mb-1 text-xs font-medium text-[var(--color-ink-muted)]">Suggested Action</div>
        <div className="rounded-lg border border-[var(--color-border)] p-3 text-sm">{prediction.suggested_action}</div>
      </div>

      <div>
        <div className="mb-1 text-xs font-medium text-[var(--color-ink-muted)]">✨ Why the AI flagged this</div>
        <div className="text-sm text-[var(--color-ink-secondary)]">{prediction.ai_explanation}</div>
      </div>

      {prediction.needs_human_review && (
        <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-700 dark:text-amber-400">
          ⚠ Flagged for human review (confidence {prediction.confidence_score}%)
        </div>
      )}

      <div className="text-xs text-[var(--color-ink-muted)]">
        Classified by {prediction.model_name} · prompt {prediction.prompt_version} · {prediction.processing_time_ms}ms
      </div>
    </div>
  )
}
