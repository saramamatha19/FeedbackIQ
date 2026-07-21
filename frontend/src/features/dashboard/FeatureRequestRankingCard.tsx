import { ChartCard } from '@/components/charts/ChartCard'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import type { DashboardData } from '@/api/types'

export function FeatureRequestRankingCard({ data, isLoading }: { data?: DashboardData; isLoading: boolean }) {
  const rows = data?.feature_request_ranking.slice(0, 6)

  return (
    <ChartCard title="Feature Request Ranking" subtitle="Ranked by volume">
      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </div>
      ) : !rows || rows.length === 0 ? (
        <EmptyState icon="✨" title="No feature requests yet" />
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
              <span className="font-medium text-blue-600">▲ {item.votes}</span>
            </li>
          ))}
        </ol>
      )}
    </ChartCard>
  )
}
