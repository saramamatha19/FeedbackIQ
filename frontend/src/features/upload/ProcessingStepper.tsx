import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useUploadStatusPolling } from './useUploadStatusPolling'

const STAGES = [
  { key: 'reading_file', label: 'Reading File' },
  { key: 'cleaning_data', label: 'Cleaning Data' },
  { key: 'removing_duplicates', label: 'Removing Duplicates' },
  { key: 'running_ai', label: 'Running AI' },
  { key: 'extracting_themes', label: 'Extracting Themes' },
  { key: 'generating_summary', label: 'Generating Summary' },
  { key: 'saving_database', label: 'Saving Database' },
  { key: 'dashboard_ready', label: 'Dashboard Ready' },
]

export function ProcessingStepper({ uploadId, onReset }: { uploadId: string; onReset: () => void }) {
  const { data: status } = useUploadStatusPolling(uploadId)

  const currentIndex = status ? STAGES.findIndex((s) => s.key === status.current_stage) : -1
  const percent = status && status.total_rows > 0 ? Math.round((status.processed_rows / status.total_rows) * 100) : 0
  const isFailed = status?.status === 'failed'
  const isComplete = status?.status === 'completed'

  return (
    <Card className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <div className="text-sm font-semibold">
            {isComplete
              ? 'Analysis complete'
              : isFailed
                ? 'Something went wrong'
                : `Analyzing ${status?.total_rows ?? '…'} feedback item(s)…`}
          </div>
          {status && status.total_rows > 0 && !isFailed && (
            <div className="text-xs text-[var(--color-ink-muted)]">
              {status.processed_rows} of {status.total_rows} processed
            </div>
          )}
        </div>
        <div className="text-lg font-semibold tabular-nums">{isComplete ? '100%' : `${percent}%`}</div>
      </div>

      <div className="relative mb-6 h-1.5 w-full overflow-hidden rounded-full bg-black/10 dark:bg-white/10">
        <motion.div
          className="h-full rounded-full bg-blue-600"
          initial={{ width: 0 }}
          animate={{ width: isFailed ? `${percent}%` : isComplete ? '100%' : `${percent}%` }}
          transition={{ type: 'spring', stiffness: 80, damping: 20 }}
          style={{ backgroundColor: isFailed ? 'var(--color-negative)' : undefined }}
        />
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {STAGES.map((stage, i) => {
          const done = currentIndex > i || isComplete
          const active = currentIndex === i && !isComplete && !isFailed
          const failedHere = isFailed && currentIndex === i
          return (
            <div key={stage.key} className="flex items-center gap-2 text-xs">
              <span
                className={
                  failedHere
                    ? 'text-red-500'
                    : done
                      ? 'text-green-600'
                      : active
                        ? 'animate-pulse text-blue-600'
                        : 'text-[var(--color-ink-muted)]'
                }
              >
                {failedHere ? '✕' : done ? '✓' : active ? '⟳' : '○'}
              </span>
              <span className={done || active ? 'text-[var(--color-ink)]' : 'text-[var(--color-ink-muted)]'}>
                {stage.label}
              </span>
            </div>
          )
        })}
      </div>

      {isFailed && (
        <div className="mt-4 space-y-3">
          <p className="text-sm text-red-500">{status?.error_message ?? 'Processing failed.'}</p>
          <Button variant="secondary" size="sm" onClick={onReset}>
            Try again
          </Button>
        </div>
      )}

      {isComplete && (
        <motion.div
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 flex items-center gap-3"
        >
          <Link to="/dashboard">
            <Button size="sm">View Dashboard →</Button>
          </Link>
          <Link to={`/history/${uploadId}`}>
            <Button variant="secondary" size="sm">
              View Upload Detail
            </Button>
          </Link>
        </motion.div>
      )}
    </Card>
  )
}
