import { ChartCard } from '@/components/charts/ChartCard'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import type { DashboardData } from '@/api/types'

const SEVERITY_DOT = ['#9ca3af', '#d97706', '#ea580c', '#dc2626']

export function BugLeaderboardCard({ data, isLoading }: { data?: DashboardData; isLoading: boolean }) {
  const rows = data?.bug_leaderboard.slice(0, 6)

  return (
    <ChartCard title="Bug Leaderboard" subtitle="Ranked by urgency & severity">
      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </div>
      ) : !rows || rows.length === 0 ? (
        <EmptyState icon="🐛" title="No bugs reported" body="Nice — nothing on the leaderboard." />
      ) : (
        <ol className="space-y-1">
          {rows.map((item, i) => (
            <li
              key={item.theme}
              className="flex items-center justify-between rounded-lg border-l-2 border-transparent px-2 py-1.5 text-sm transition-colors hover:border-blue-500 hover:bg-black/5 dark:hover:bg-white/5"
            >
              <span className="flex items-center gap-2">
                <span className="text-xs text-[var(--color-ink-muted)]">{i + 1}.</span>
                {item.theme}
              </span>
              <span className="flex items-center gap-1.5 font-medium">
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: SEVERITY_DOT[Math.min(item.max_severity - 1, 3)] ?? '#9ca3af' }}
                />
                {item.occurrences}
              </span>
            </li>
          ))}
        </ol>
      )}
    </ChartCard>
  )
}
