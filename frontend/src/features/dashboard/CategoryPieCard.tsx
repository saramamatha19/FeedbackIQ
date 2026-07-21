import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { ChartCard, ChartTooltip } from '@/components/charts/ChartCard'
import { ChartSkeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { CATEGORY_COLORS, CATEGORY_ICONS } from '@/lib/constants'
import type { DashboardData } from '@/api/types'

export function CategoryPieCard({ data, isLoading }: { data?: DashboardData; isLoading: boolean }) {
  const rows = data?.category_breakdown ?? []
  const total = rows.reduce((sum, r) => sum + r.count, 0)

  return (
    <ChartCard title="Category Breakdown">
      {isLoading ? (
        <ChartSkeleton />
      ) : rows.length === 0 ? (
        <EmptyState icon="📊" title="No data yet" />
      ) : (
        <div className="flex items-center gap-4">
          <ResponsiveContainer width="45%" height={180}>
            <PieChart>
              <Pie data={rows} dataKey="count" nameKey="category" innerRadius={45} outerRadius={75} paddingAngle={2}>
                {rows.map((entry) => (
                  <Cell key={entry.category} fill={CATEGORY_COLORS[entry.category] ?? 'var(--cat-other)'} />
                ))}
              </Pie>
              <Tooltip content={<ChartTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <ul className="flex-1 space-y-2">
            {rows.map((entry) => (
              <li key={entry.category} className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-2">
                  <span
                    className="h-2.5 w-2.5 shrink-0 rounded-full"
                    style={{ backgroundColor: CATEGORY_COLORS[entry.category] ?? 'var(--cat-other)' }}
                  />
                  <span>
                    {CATEGORY_ICONS[entry.category] ?? '📋'} {entry.category}
                  </span>
                </span>
                <span className="font-medium tabular-nums text-[var(--color-ink-secondary)]">
                  {entry.count} · {total ? Math.round((entry.count / total) * 100) : 0}%
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </ChartCard>
  )
}
