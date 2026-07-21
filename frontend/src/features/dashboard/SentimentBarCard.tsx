import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis } from 'recharts'
import { ChartCard, ChartTooltip } from '@/components/charts/ChartCard'
import { ChartSkeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { SENTIMENT_COLORS } from '@/lib/constants'
import type { DashboardData } from '@/api/types'

export function SentimentBarCard({ data, isLoading }: { data?: DashboardData; isLoading: boolean }) {
  return (
    <ChartCard title="Sentiment Distribution">
      {isLoading ? (
        <ChartSkeleton />
      ) : !data || data.sentiment_distribution.length === 0 ? (
        <EmptyState icon="💬" title="No data yet" />
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data.sentiment_distribution}>
            <XAxis dataKey="sentiment" tickLine={false} axisLine={false} fontSize={12} />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: 'transparent' }} />
            <Bar dataKey="count" radius={[6, 6, 0, 0]}>
              {data.sentiment_distribution.map((entry) => (
                <Cell key={entry.sentiment} fill={SENTIMENT_COLORS[entry.sentiment] ?? 'var(--color-neutral)'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  )
}
