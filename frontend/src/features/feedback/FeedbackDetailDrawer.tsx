import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Drawer } from '@/components/ui/Drawer'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/Skeleton'
import { useUiStore } from '@/store/uiStore'
import { fetchFeedbackById, rerunFeedback } from '@/api/feedback'
import { fetchFeedbackByIdAsAdmin } from '@/api/admin'
import { formatDateTime } from '@/lib/formatters'
import { PredictionSummary } from '@/features/feedback/PredictionSummary'

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
                <PredictionSummary prediction={prediction} />

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
