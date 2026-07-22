import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'
import { approveUser, fetchAdminDashboard, fetchAllUsers, fetchUsageStats, rejectUser } from '@/api/admin'
import { apiErrorMessage } from '@/api/client'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
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
  const queryClient = useQueryClient()
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

  const approve = useMutation({
    mutationFn: approveUser,
    onSuccess: () => {
      toast.success('User approved.')
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: (err) => toast.error(apiErrorMessage(err, 'Could not approve user.')),
  })
  const reject = useMutation({
    mutationFn: rejectUser,
    onSuccess: () => {
      toast.success('User rejected.')
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: (err) => toast.error(apiErrorMessage(err, 'Could not reject user.')),
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
          <KpiRow data={dashboard?.data} isLoading={dashboardLoading} showSeverity={false} />
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
          <div className="max-h-60 overflow-y-auto">
          <table className="w-full text-left text-sm">
            <thead className="sticky top-0 bg-[var(--color-surface)]">
              <tr className="border-b border-[var(--color-border)] text-xs text-[var(--color-ink-muted)]">
                <th className="py-2 pr-3 font-medium">Email</th>
                <th className="py-2 pr-3 font-medium">Name</th>
                <th className="py-2 pr-3 font-medium">Role</th>
                <th className="py-2 pr-3 font-medium">Status</th>
                <th className="py-2 pr-3 font-medium">Joined</th>
                <th className="py-2 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users?.map((u) => {
                const pending = u.is_active && !u.is_approved && u.role !== 'admin'
                const rejected = !u.is_active
                return (
                  <tr
                    key={u.id}
                    className="border-b border-[var(--color-border)] last:border-0 hover:bg-black/5 dark:hover:bg-white/5"
                  >
                    <td className="py-2.5 pr-3">
                      <Link to={`/admin/users/${u.id}`} className="text-blue-600 hover:underline">
                        {u.email}
                      </Link>
                    </td>
                    <td className="py-2.5 pr-3 text-[var(--color-ink-secondary)]">{u.full_name ?? '—'}</td>
                    <td className="py-2.5 pr-3">{u.role}</td>
                    <td className="py-2.5 pr-3">
                      {rejected ? (
                        <span className="text-xs font-medium text-red-500">Rejected</span>
                      ) : pending ? (
                        <span className="text-xs font-medium text-amber-500">Pending</span>
                      ) : (
                        <span className="text-xs font-medium text-green-600">Approved</span>
                      )}
                    </td>
                    <td className="py-2.5 pr-3 text-xs text-[var(--color-ink-muted)]">{formatDate(u.created_at)}</td>
                    <td className="py-2.5">
                      {pending && (
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            disabled={approve.isPending}
                            onClick={() => approve.mutate(u.id)}
                          >
                            Approve
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            disabled={reject.isPending}
                            onClick={() => reject.mutate(u.id)}
                          >
                            Reject
                          </Button>
                        </div>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
          </div>
        )}
      </Card>
    </div>
  )
}
