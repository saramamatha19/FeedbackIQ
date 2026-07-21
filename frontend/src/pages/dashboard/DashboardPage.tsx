import { motion } from 'framer-motion'
import { useDashboardData } from '@/features/dashboard/useDashboardData'
import { KpiRow } from '@/features/dashboard/KpiRow'
import { KeySignalsCard } from '@/features/dashboard/KeySignalsCard'
import { CategoryPieCard } from '@/features/dashboard/CategoryPieCard'
import { SentimentBarCard } from '@/features/dashboard/SentimentBarCard'
import { EmotionDistributionCard } from '@/features/dashboard/EmotionDistributionCard'
import { TopThemesCard } from '@/features/dashboard/TopThemesCard'
import { FeatureRequestRankingCard } from '@/features/dashboard/FeatureRequestRankingCard'
import { BugLeaderboardCard } from '@/features/dashboard/BugLeaderboardCard'
import { FeedbackTable } from '@/features/feedback/FeedbackTable'

function Section({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay }}>
      {children}
    </motion.div>
  )
}

export function DashboardPage() {
  const { data, isLoading } = useDashboardData()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Dashboard</h1>
        <p className="text-sm text-[var(--color-ink-muted)]">All-time overview across every upload.</p>
      </div>

      <KpiRow data={data?.data} isLoading={isLoading} />

      <Section delay={0.1}>
        <KeySignalsCard data={data?.data} isLoading={isLoading} />
      </Section>

      <Section delay={0.15}>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <CategoryPieCard data={data?.data} isLoading={isLoading} />
          <SentimentBarCard data={data?.data} isLoading={isLoading} />
          <EmotionDistributionCard data={data?.data} isLoading={isLoading} />
        </div>
      </Section>

      <Section delay={0.2}>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <TopThemesCard data={data?.data} isLoading={isLoading} />
          <FeatureRequestRankingCard data={data?.data} isLoading={isLoading} />
          <BugLeaderboardCard data={data?.data} isLoading={isLoading} />
        </div>
      </Section>

      <Section delay={0.25}>
        <FeedbackTable />
      </Section>
    </div>
  )
}
