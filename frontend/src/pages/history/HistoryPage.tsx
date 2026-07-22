import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { Button } from '@/components/ui/Button'
import { fetchUploads } from '@/api/uploads'
import { formatDateTime } from '@/lib/formatters'

const STATUS_COLOR: Record<string, string> = {
  completed: 'text-green-600',
  processing: 'text-blue-600',
  pending: 'text-[var(--color-ink-muted)]',
  failed: 'text-red-500',
  partial: 'text-amber-500',
}

const SOURCE_LABEL: Record<string, string> = { single: 'Single', paste: 'Paste', csv: 'CSV', xlsx: 'Excel' }

export function HistoryPage() {
  const { data, isLoading } = useQuery({ queryKey: ['uploads'], queryFn: () => fetchUploads() })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">History</h1>
        <Link to="/upload">
          <Button size="sm">+ New Upload</Button>
        </Link>
      </div>

      <Card className="p-5">
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        ) : !data || data.length === 0 ? (
          <EmptyState
            icon="🗂️"
            title="No uploads yet"
            body="Every upload becomes an analysis session you can revisit here."
            action={
              <Link to="/upload">
                <Button size="sm">Upload your first batch</Button>
              </Link>
            }
          />
        ) : (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border)] text-xs text-[var(--color-ink-muted)]">
                <th className="py-2 pr-3 font-medium">Source</th>
                <th className="py-2 pr-3 font-medium">Filename</th>
                <th className="py-2 pr-3 font-medium">Items</th>
                <th className="py-2 pr-3 font-medium">Status</th>
                <th className="py-2 font-medium">Created</th>
              </tr>
            </thead>
            <tbody>
              {data.map((upload) => (
                <tr key={upload.id} className="border-b border-[var(--color-border)] last:border-0">
                  <td className="py-2.5 pr-3">
                    <Link to={`/history/${upload.id}`} className="hover:underline">
                      {SOURCE_LABEL[upload.source_type]}
                    </Link>
                  </td>
                  <td className="py-2.5 pr-3 text-[var(--color-ink-secondary)]">
                    {upload.original_filename ?? '—'}
                  </td>
                  <td className="py-2.5 pr-3 tabular-nums">{upload.total_rows}</td>
                  <td className={`py-2.5 pr-3 font-medium ${STATUS_COLOR[upload.status]}`}>{upload.status}</td>
                  <td className="py-2.5 text-xs text-[var(--color-ink-muted)]">
                    {formatDateTime(upload.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  )
}
