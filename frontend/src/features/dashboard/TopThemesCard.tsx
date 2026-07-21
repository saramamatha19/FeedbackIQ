import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { ChartCard, ChartTooltip } from '@/components/charts/ChartCard'
import { ChartSkeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import type { DashboardData } from '@/api/types'

export function TopThemesCard({ data, isLoading }: { data?: DashboardData; isLoading: boolean }) {
  const rows = data?.top_themes.slice(0, 5)

  return (
    <ChartCard title="Top Themes">
      {isLoading ? (
        <ChartSkeleton />
      ) : !rows || rows.length === 0 ? (
        <EmptyState icon="🏷️" title="No themes yet" />
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={rows} layout="vertical" margin={{ left: 12 }}>
            <CartesianGrid horizontal={false} stroke="var(--color-grid)" />
            <XAxis type="number" hide />
            <YAxis type="category" dataKey="theme" width={130} tickLine={false} axisLine={false} fontSize={11} />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: 'transparent' }} />
            <Bar dataKey="count" fill="var(--color-accent)" radius={[0, 6, 6, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  )
}
