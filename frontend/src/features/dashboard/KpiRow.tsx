import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import type { DashboardData } from '@/api/types'

function Tile({ label, value, index, accent }: { label: string; value: string | number; index: number; accent?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: index * 0.06, ease: [0.16, 1, 0.3, 1] }}
    >
      <Card className="p-5">
        <div className="text-xs font-medium text-[var(--color-ink-muted)]">{label}</div>
        <div className="mt-2 text-2xl font-semibold tabular-nums" style={{ color: accent }}>
          {value}
        </div>
      </Card>
    </motion.div>
  )
}

export function KpiRow({ data, isLoading }: { data?: DashboardData; isLoading: boolean }) {
  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="p-5">
            <Skeleton className="h-3 w-20" />
            <Skeleton className="mt-3 h-7 w-16" />
          </Card>
        ))}
      </div>
    )
  }

  const { overview } = data

  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
      <Tile label="Total Feedback" value={overview.total_feedback} index={0} />
      <Tile label="Urgent Items" value={overview.urgent} index={1} accent="var(--color-urgent)" />
      <Tile label="Avg Confidence" value={`${overview.avg_confidence}%`} index={2} />
      <Tile label="Avg Severity" value={`${overview.avg_severity}/10`} index={3} />
    </div>
  )
}
