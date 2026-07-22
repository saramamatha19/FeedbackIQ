import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { useMe } from '@/lib/useAuth'
import { formatDateTime } from '@/lib/formatters'

function initialsOf(name: string | null, email: string): string {
  if (name && name.trim()) {
    const parts = name.trim().split(/\s+/)
    return (parts[0][0] + (parts[1]?.[0] ?? '')).toUpperCase()
  }
  return email[0]?.toUpperCase() ?? '?'
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between border-b border-[var(--color-border)] py-3 last:border-0">
      <span className="text-xs font-medium text-[var(--color-ink-muted)]">{label}</span>
      <span className="text-sm font-medium">{value}</span>
    </div>
  )
}

export function ProfilePage() {
  const { data: user, isLoading } = useMe()

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Profile</h1>
        <p className="text-sm text-[var(--color-ink-muted)]">Your account details.</p>
      </div>

      <Card className="p-6">
        {isLoading || !user ? (
          <div className="space-y-4">
            <Skeleton className="h-16 w-16 rounded-full" />
            <Skeleton className="h-4 w-40" />
            <Skeleton className="h-4 w-56" />
          </div>
        ) : (
          <>
            <div className="mb-5 flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-blue-600/10 text-lg font-semibold text-blue-600">
                {initialsOf(user.full_name, user.email)}
              </div>
              <div>
                <div className="text-base font-semibold">{user.full_name ?? 'No name set'}</div>
                <div className="text-sm text-[var(--color-ink-muted)]">{user.email}</div>
              </div>
            </div>

            <div>
              <Row label="Role" value={<span className="capitalize">{user.role}</span>} />
              <Row
                label="Account status"
                value={
                  !user.is_active ? (
                    <span className="text-red-500">Rejected</span>
                  ) : user.role === 'admin' || user.is_approved ? (
                    <span className="text-green-600">Approved</span>
                  ) : (
                    <span className="text-amber-500">Pending approval</span>
                  )
                }
              />
              <Row label="Joined" value={formatDateTime(user.created_at)} />
            </div>
          </>
        )}
      </Card>
    </div>
  )
}
