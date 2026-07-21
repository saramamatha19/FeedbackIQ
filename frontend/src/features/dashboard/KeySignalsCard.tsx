import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import type { DashboardData } from '@/api/types'

const SEVERITY_ICON: Record<string, string> = { info: 'ℹ️', watch: '👀', urgent: '🚨' }

export function KeySignalsCard({ data, isLoading }: { data?: DashboardData; isLoading: boolean }) {
  return (
    <Card className="p-5">
      <div className="mb-3 flex items-center gap-2">
        <span className="text-sm font-semibold">✨ This Week's Key Signals</span>
      </div>
      {isLoading || !data ? (
        <div className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <Skeleton className="h-4 w-4/6" />
        </div>
      ) : (
        <ul className="space-y-3">
          {data.key_signals.map((signal, i) => (
            <motion.li
              key={i}
              initial={{ opacity: 0, x: -4 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              className="flex gap-2 text-sm"
            >
              <span>{SEVERITY_ICON[signal.severity_hint] ?? 'ℹ️'}</span>
              <span>
                <span className="font-medium">{signal.headline}</span>
                <span className="text-[var(--color-ink-secondary)]"> — {signal.detail}</span>
              </span>
            </motion.li>
          ))}
        </ul>
      )}
    </Card>
  )
}
