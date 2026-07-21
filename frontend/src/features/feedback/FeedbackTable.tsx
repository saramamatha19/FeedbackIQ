import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { exportFeedbackCsvUrl, fetchFeedback } from '@/api/feedback'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { Button } from '@/components/ui/Button'
import { SentimentPill } from './SentimentPill'
import { CATEGORY_ICONS, URGENCY_STYLES } from '@/lib/constants'
import { formatDate, truncate } from '@/lib/formatters'
import { useUiStore } from '@/store/uiStore'

export function FeedbackTable({ uploadId, title = 'Recent Feedback' }: { uploadId?: string; title?: string }) {
  const [search, setSearch] = useState('')
  const openDrawer = useUiStore((s) => s.openFeedbackDrawer)

  const { data, isLoading } = useQuery({
    queryKey: ['feedback-list', uploadId],
    queryFn: () => fetchFeedback({ upload_id: uploadId, limit: 100 }),
  })

  const filtered = (data ?? []).filter((row) =>
    search ? row.raw_text.toLowerCase().includes(search.toLowerCase()) : true,
  )

  return (
    <Card className="p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold">{title}</h3>
        <div className="flex items-center gap-2">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search within table…"
            className="rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-1.5 text-xs outline-none focus:border-blue-500"
          />
          <a href={exportFeedbackCsvUrl(uploadId)} target="_blank" rel="noreferrer">
            <Button variant="secondary" size="sm">
              ⤓ CSV
            </Button>
          </a>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-full" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon="📭"
          title="Nothing here yet"
          body="Upload your first batch of feedback to see it show up here."
        />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border)] text-xs text-[var(--color-ink-muted)]">
                <th className="py-2 pr-3 font-medium">Date</th>
                <th className="py-2 pr-3 font-medium">Category</th>
                <th className="py-2 pr-3 font-medium">Sentiment</th>
                <th className="py-2 pr-3 font-medium">Urgency</th>
                <th className="py-2 pr-3 font-medium">Theme</th>
                <th className="py-2 font-medium">Preview</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((row) => (
                <tr
                  key={row.id}
                  onClick={() => openDrawer(row.id)}
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
                  <td className="py-2.5 text-[var(--color-ink-secondary)]">
                    {truncate(row.raw_text, 60)} →
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  )
}
