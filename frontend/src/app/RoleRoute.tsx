import { Navigate, Outlet } from 'react-router-dom'
import { useMe } from '@/lib/useAuth'

export function RoleHome() {
  const { data: user } = useMe()
  return <Navigate to={user?.role === 'admin' ? '/admin' : '/dashboard'} replace />
}

export function AdminRoute() {
  const { data: user } = useMe()
  if (user?.role !== 'admin') return <Navigate to="/dashboard" replace />
  return <Outlet />
}

export function UserRoute() {
  const { data: user } = useMe()
  if (user?.role === 'admin') return <Navigate to="/admin" replace />
  return <Outlet />
}
