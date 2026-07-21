import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { ChartCard, ChartTooltip } from '@/components/charts/ChartCard'
import { ChartSkeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { EMOTION_EMOJI } from '@/lib/constants'
import type { DashboardData } from '@/api/types'

export function EmotionDistributionCard({ data, isLoading }: { data?: DashboardData; isLoading: boolean }) {
  const rows = data?.emotion_distribution.map((e) => ({
    ...e,
    label: `${EMOTION_EMOJI[e.emotion] ?? ''} ${e.emotion}`,
  }))

  return (
    <ChartCard title="Emotion Distribution">
      {isLoading ? (
        <ChartSkeleton />
      ) : !rows || rows.length === 0 ? (
        <EmptyState icon="🎭" title="No data yet" />
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={rows} layout="vertical" margin={{ left: 12 }}>
            <CartesianGrid horizontal={false} stroke="var(--color-grid)" />
            <XAxis type="number" hide />
            <YAxis type="category" dataKey="label" width={110} tickLine={false} axisLine={false} fontSize={12} />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: 'transparent' }} />
            <Bar dataKey="count" fill="var(--color-accent)" radius={[0, 6, 6, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  )
}
