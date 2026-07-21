import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Drawer } from '@/components/ui/Drawer'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { useUiStore } from '@/store/uiStore'
import { fetchFeedbackById, rerunFeedback } from '@/api/feedback'
import { fetchFeedbackByIdAsAdmin } from '@/api/admin'
import { formatDateTime } from '@/lib/formatters'
import {
  BUSINESS_IMPACT_FILL,
  CATEGORY_COLORS,
  CATEGORY_ICONS,
  EMOTION_EMOJI,
  SENTIMENT_COLORS,
  SEVERITY_FILL,
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

export function FeedbackDetailDrawer() {
  const selectedId = useUiStore((s) => s.selectedFeedbackId)
  const scope = useUiStore((s) => s.selectedFeedbackScope)
  const close = useUiStore((s) => s.closeFeedbackDrawer)
  const queryClient = useQueryClient()
  const isAdminScope = scope === 'admin'

  const { data: feedback, isLoading } = useQuery({
    queryKey: ['feedback', scope, selectedId],
    queryFn: () =>
      isAdminScope ? fetchFeedbackByIdAsAdmin(selectedId as string) : fetchFeedbackById(selectedId as string),
    enabled: !!selectedId,
  })

  const rerun = useMutation({
    mutationFn: () => rerunFeedback(selectedId as string),
    onSuccess: () => {
      toast.success('Re-analyzed with the latest prompt version.')
      queryClient.invalidateQueries({ queryKey: ['feedback', selectedId] })
      queryClient.invalidateQueries({ queryKey: ['feedback-list'] })
    },
    onError: () => toast.error('Re-run failed. Please try again.'),
  })

  const prediction = feedback?.prediction

  return (
    <Drawer open={!!selectedId} onClose={close}>
      <div className="flex items-center justify-between border-b border-[var(--color-border)] px-5 py-4">
        <h2 className="text-sm font-semibold">Feedback Detail</h2>
        <button onClick={close} className="text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]">
          ✕
        </button>
      </div>

      <div className="space-y-5 p-5">
        {isLoading || !feedback ? (
          <div className="space-y-3">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
        ) : (
          <>
            <div className="text-xs text-[var(--color-ink-muted)]">{formatDateTime(feedback.created_at)}</div>
            <p className="rounded-lg bg-black/[0.03] p-3 text-sm leading-relaxed dark:bg-white/5">
              "{feedback.raw_text}"
            </p>

            {prediction ? (
              <>
                <div className="flex flex-wrap gap-2">
                  <Badge color={CATEGORY_COLORS[prediction.category] ?? '#9ca3af'}>
                    {CATEGORY_ICONS[prediction.category] ?? '📋'} {prediction.category}
                  </Badge>
                  <Badge color={SENTIMENT_COLORS[prediction.sentiment]}>{prediction.sentiment}</Badge>
                  <Badge color="#9ca3af">
                    {EMOTION_EMOJI[prediction.emotion] ?? ''} {prediction.emotion}
                  </Badge>
                  <Badge color={URGENCY_STYLES[prediction.urgency]?.color ?? '#9ca3af'}>
                    {prediction.urgency}
                  </Badge>
                </div>

                <div className="text-sm">
                  <span className="text-[var(--color-ink-muted)]">Theme: </span>
                  <span className="font-medium">{prediction.theme}</span>
                </div>

                <div className="space-y-3">
                  <Meter
                    label={`Severity — ${prediction.severity}`}
                    fraction={SEVERITY_FILL[prediction.severity] ?? 0.25}
                    color="var(--color-accent)"
                  />
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
                  <div className="rounded-lg border border-[var(--color-border)] p-3 text-sm">
                    {prediction.suggested_action}
                  </div>
                </div>

                <div>
                  <div className="mb-1 text-xs font-medium text-[var(--color-ink-muted)]">
                    ✨ Why the AI flagged this
                  </div>
                  <div className="text-sm text-[var(--color-ink-secondary)]">{prediction.ai_explanation}</div>
                </div>

                {prediction.needs_human_review && (
                  <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-700 dark:text-amber-400">
                    ⚠ Flagged for human review (confidence {prediction.confidence_score}%)
                  </div>
                )}

                <div className="text-xs text-[var(--color-ink-muted)]">
                  Classified by {prediction.model_name} · prompt {prediction.prompt_version} ·{' '}
                  {prediction.processing_time_ms}ms
                </div>

                {!isAdminScope && (
                  <Button variant="secondary" size="sm" onClick={() => rerun.mutate()} disabled={rerun.isPending}>
                    {rerun.isPending ? 'Re-analyzing…' : '↻ Re-run AI analysis'}
                  </Button>
                )}
              </>
            ) : (
              <div className="text-sm text-[var(--color-ink-muted)]">Still processing…</div>
            )}
          </>
        )}
      </div>
    </Drawer>
  )
}
