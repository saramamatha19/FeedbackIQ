import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { exportFeedbackCsvUrl, fetchFeedback } from '@/api/feedback'
import { deleteFeedbackAsAdmin } from '@/api/admin'
import { apiErrorMessage } from '@/api/client'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { Button } from '@/components/ui/Button'
import { SentimentPill } from './SentimentPill'
import { CANONICAL_THEMES, CATEGORY_ICONS, SENTIMENT_COLORS, URGENCY_STYLES } from '@/lib/constants'
import { formatDate, truncate } from '@/lib/formatters'
import { useUiStore } from '@/store/uiStore'
import type { Feedback } from '@/api/types'

const ALL = 'All'

function FilterSelect({
  label,
  value,
  onChange,
  options,
}: {
  label: string
  value: string
  onChange: (value: string) => void
  options: string[]
}) {
  return (
    <select
      aria-label={label}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-lg border border-[var(--color-border)] bg-transparent px-2 py-1.5 text-xs outline-none focus:border-blue-500"
    >
      <option value={ALL}>{label}: All</option>
      {options.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  )
}

export function FeedbackTable({
  uploadId,
  title = 'Recent Feedback',
  queryKey,
  queryFn,
  feedbackScope = 'own',
  showExport = true,
}: {
  uploadId?: string
  title?: string
  queryKey?: unknown[]
  queryFn?: () => Promise<Feedback[]>
  feedbackScope?: 'own' | 'admin'
  showExport?: boolean
}) {
  const [category, setCategory] = useState(ALL)
  const [sentiment, setSentiment] = useState(ALL)
  const [urgency, setUrgency] = useState(ALL)
  const [theme, setTheme] = useState(ALL)
  const openDrawer = useUiStore((s) => s.openFeedbackDrawer)
  const queryClient = useQueryClient()
  const resolvedQueryKey = queryKey ?? ['feedback-list', uploadId]

  const { data, isLoading } = useQuery({
    queryKey: resolvedQueryKey,
    queryFn: queryFn ?? (() => fetchFeedback({ upload_id: uploadId, limit: 100 })),
  })

  const deleteRow = useMutation({
    mutationFn: deleteFeedbackAsAdmin,
    onSuccess: () => {
      toast.success('Feedback deleted.')
      queryClient.invalidateQueries({ queryKey: resolvedQueryKey })
    },
    onError: (err) => toast.error(apiErrorMessage(err, 'Could not delete feedback.')),
  })

  const filtered = useMemo(
    () =>
      (data ?? []).filter((row) => {
        if (category !== ALL && row.prediction?.category !== category) return false
        if (sentiment !== ALL && row.prediction?.sentiment !== sentiment) return false
        if (urgency !== ALL && row.prediction?.urgency !== urgency) return false
        if (theme !== ALL && row.prediction?.theme !== theme) return false
        return true
      }),
    [data, category, sentiment, urgency, theme],
  )

  const hasAnyFeedback = (data ?? []).length > 0
  const hasActiveFilter = [category, sentiment, urgency, theme].some((f) => f !== ALL)

  return (
    <Card className="p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold">{title}</h3>
        <div className="flex flex-wrap items-center gap-2">
          <FilterSelect label="Category" value={category} onChange={setCategory} options={Object.keys(CATEGORY_ICONS)} />
          <FilterSelect label="Sentiment" value={sentiment} onChange={setSentiment} options={Object.keys(SENTIMENT_COLORS)} />
          <FilterSelect label="Urgency" value={urgency} onChange={setUrgency} options={Object.keys(URGENCY_STYLES)} />
          <FilterSelect label="Theme" value={theme} onChange={setTheme} options={CANONICAL_THEMES} />
          {showExport && (
            <a href={exportFeedbackCsvUrl(uploadId)} target="_blank" rel="noreferrer">
              <Button variant="secondary" size="sm">
                ⤓ CSV
              </Button>
            </a>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-full" />
          ))}
        </div>
      ) : !hasAnyFeedback ? (
        <EmptyState
          icon="📭"
          title="Nothing here yet"
          body="Upload your first batch of feedback to see it show up here."
        />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon="🔍"
          title="No matches"
          body="No feedback matches the selected filters. Try clearing one."
        />
      ) : (
        <div className="max-h-80 overflow-y-auto overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="sticky top-0 bg-[var(--color-surface)]">
              <tr className="border-b border-[var(--color-border)] text-xs text-[var(--color-ink-muted)]">
                <th className="py-2 pr-3 font-medium">Date</th>
                <th className="py-2 pr-3 font-medium">Category</th>
                <th className="py-2 pr-3 font-medium">Sentiment</th>
                <th className="py-2 pr-3 font-medium">Urgency</th>
                <th className="py-2 pr-3 font-medium">Theme</th>
                <th className="py-2 pr-3 font-medium">Source</th>
                <th className="py-2 pr-3 font-medium">Preview</th>
                {feedbackScope === 'admin' && <th className="py-2 font-medium">Actions</th>}
              </tr>
            </thead>
            <tbody>
              {filtered.map((row) => (
                <tr
                  key={row.id}
                  onClick={() => openDrawer(row.id, feedbackScope)}
                  className="cursor-pointer border-b border-[var(--color-border)] last:border-0 hover:bg-black/5 dark:hover:bg-white/5"
                >
                  <td className="py-2.5 pr-3 text-xs text-[var(--color-ink-muted)] tabular-nums">
                    {formatDate(row.created_at)}
                  </td>
                  <td className="py-2.5 pr-3">
                    {row.prediction ? (
                      <span>
                        {CATEGORY_ICONS[row.prediction.category] ?? '📋'} {row.prediction.category}
                      </span>
                    ) : (
                      <span className="text-xs text-[var(--color-ink-muted)]">processing…</span>
                    )}
                  </td>
                  <td className="py-2.5 pr-3">
                    {row.prediction && <SentimentPill sentiment={row.prediction.sentiment} />}
                  </td>
                  <td className="py-2.5 pr-3">
                    {row.prediction && (
                      <span
                        className="text-xs font-medium"
                        style={{ color: URGENCY_STYLES[row.prediction.urgency]?.color }}
                      >
                        {row.prediction.urgency}
                      </span>
                    )}
                  </td>
                  <td className="py-2.5 pr-3 text-xs">{row.prediction?.theme ?? '—'}</td>
                  <td className="py-2.5 pr-3 text-xs text-[var(--color-ink-muted)]">{row.source_label || '—'}</td>
                  <td className="py-2.5 pr-3 text-[var(--color-ink-secondary)]">
                    {truncate(row.raw_text, 60)} →
                  </td>
                  {feedbackScope === 'admin' && (
                    <td className="py-2.5">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          if (window.confirm('Delete this feedback entry? This cannot be undone.')) {
                            deleteRow.mutate(row.id)
                          }
                        }}
                        disabled={deleteRow.isPending}
                        className="text-xs font-medium text-red-500 hover:underline disabled:opacity-50"
                      >
                        Delete
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {hasActiveFilter && filtered.length > 0 && (
        <p className="mt-2 text-xs text-[var(--color-ink-muted)]">
          Showing {filtered.length} of {data?.length ?? 0}
        </p>
      )}
    </Card>
  )
}
