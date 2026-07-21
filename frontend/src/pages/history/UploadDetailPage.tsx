import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchUpload } from '@/api/uploads'
import { useDashboardData } from '@/features/dashboard/useDashboardData'
import { KpiRow } from '@/features/dashboard/KpiRow'
import { CategoryPieCard } from '@/features/dashboard/CategoryPieCard'
import { SentimentBarCard } from '@/features/dashboard/SentimentBarCard'
import { FeedbackTable } from '@/features/feedback/FeedbackTable'
import { formatDateTime } from '@/lib/formatters'

export function UploadDetailPage() {
  const { uploadId } = useParams<{ uploadId: string }>()
  const { data: upload } = useQuery({
    queryKey: ['upload', uploadId],
    queryFn: () => fetchUpload(uploadId as string),
    enabled: !!uploadId,
  })
  const { data: dashboard, isLoading } = useDashboardData(uploadId)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">
          {upload?.original_filename ?? upload?.source_type ?? 'Upload'}
        </h1>
        {upload && (
          <p className="text-sm text-[var(--color-ink-muted)]">
            {upload.total_rows} items · uploaded {formatDateTime(upload.created_at)}
          </p>
        )}
      </div>

      <KpiRow data={dashboard?.data} isLoading={isLoading} />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <CategoryPieCard data={dashboard?.data} isLoading={isLoading} />
        <SentimentBarCard data={dashboard?.data} isLoading={isLoading} />
      </div>

      <FeedbackTable uploadId={uploadId} title="Feedback in this upload" />
    </div>
  )
}
