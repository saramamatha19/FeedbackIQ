import { useQuery } from '@tanstack/react-query'
import { fetchAdminDashboard, fetchAllUsers, fetchUsageStats } from '@/api/admin'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { formatDate } from '@/lib/formatters'
import { KpiRow } from '@/features/dashboard/KpiRow'
import { KeySignalsCard } from '@/features/dashboard/KeySignalsCard'
import { CategoryPieCard } from '@/features/dashboard/CategoryPieCard'
import { SentimentBarCard } from '@/features/dashboard/SentimentBarCard'
import { EmotionDistributionCard } from '@/features/dashboard/EmotionDistributionCard'
import { TopThemesCard } from '@/features/dashboard/TopThemesCard'
import { FeatureRequestRankingCard } from '@/features/dashboard/FeatureRequestRankingCard'
import { BugLeaderboardCard } from '@/features/dashboard/BugLeaderboardCard'

function StatTile({ label, value }: { label: string; value: string | number }) {
  return (
    <Card className="p-5">
      <div className="text-xs font-medium text-[var(--color-ink-muted)]">{label}</div>
      <div className="mt-2 text-2xl font-semibold tabular-nums">{value}</div>
    </Card>
  )
}

export function AdminPage() {
  const { data: usage, isLoading: usageLoading } = useQuery({
    queryKey: ['admin-usage'],
    queryFn: fetchUsageStats,
  })
  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: fetchAllUsers,
  })
  const { data: dashboard, isLoading: dashboardLoading } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: fetchAdminDashboard,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Admin</h1>
        <p className="text-sm text-[var(--color-ink-muted)]">Cross-user analysis across every account.</p>
      </div>

      {usageLoading || !usage ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="p-5">
              <Skeleton className="h-3 w-20" />
              <Skeleton className="mt-3 h-7 w-16" />
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
          <StatTile label="Total Users" value={usage.total_users} />
          <StatTile label="Total Uploads" value={usage.total_uploads} />
          <StatTile label="Total Feedback" value={usage.total_feedback} />
          <StatTile label="Avg Confidence" value={`${usage.avg_confidence ?? 0}%`} />
          <StatTile label="Avg Processing Time" value={`${usage.avg_processing_time_ms ?? 0}ms`} />
          <StatTile label="Needs Review" value={usage.needs_review_count} />
        </div>
      )}

      <div>
        <h2 className="mb-3 text-sm font-semibold">Feedback analysis (all users)</h2>
        <div className="space-y-6">
          <KpiRow data={dashboard?.data} isLoading={dashboardLoading} />
          <KeySignalsCard data={dashboard?.data} isLoading={dashboardLoading} />
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <CategoryPieCard data={dashboard?.data} isLoading={dashboardLoading} />
            <SentimentBarCard data={dashboard?.data} isLoading={dashboardLoading} />
            <EmotionDistributionCard data={dashboard?.data} isLoading={dashboardLoading} />
          </div>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <TopThemesCard data={dashboard?.data} isLoading={dashboardLoading} />
            <FeatureRequestRankingCard data={dashboard?.data} isLoading={dashboardLoading} />
            <BugLeaderboardCard data={dashboard?.data} isLoading={dashboardLoading} />
          </div>
        </div>
      </div>

      <Card className="p-5">
        <h2 className="mb-3 text-sm font-semibold">Users</h2>
        {usersLoading ? (
          <Skeleton className="h-24 w-full" />
        ) : (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border)] text-xs text-[var(--color-ink-muted)]">
                <th className="py-2 pr-3 font-medium">Email</th>
                <th className="py-2 pr-3 font-medium">Name</th>
                <th className="py-2 pr-3 font-medium">Role</th>
                <th className="py-2 font-medium">Joined</th>
              </tr>
            </thead>
            <tbody>
              {users?.map((u) => (
                <tr key={u.id} className="border-b border-[var(--color-border)] last:border-0">
                  <td className="py-2.5 pr-3">{u.email}</td>
                  <td className="py-2.5 pr-3 text-[var(--color-ink-secondary)]">{u.full_name ?? '—'}</td>
                  <td className="py-2.5 pr-3">{u.role}</td>
                  <td className="py-2.5 text-xs text-[var(--color-ink-muted)]">{formatDate(u.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  )
}
