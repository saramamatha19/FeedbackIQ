import { Navigate, Outlet } from 'react-router-dom'
import { useMe } from '@/lib/useAuth'

export function ProtectedRoute() {
  const { data: user, isLoading, isError } = useMe()

  if (isLoading) {
    return <div className="flex min-h-screen items-center justify-center text-sm text-[var(--color-ink-muted)]">Loading…</div>
  }

  if (isError || !user) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
