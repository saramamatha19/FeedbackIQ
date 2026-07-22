import { NavLink, Outlet } from 'react-router-dom'
import clsx from 'clsx'
import { ThemeToggle } from '@/components/ui/ThemeToggle'
import { FeedbackDetailDrawer } from '@/features/feedback/FeedbackDetailDrawer'
import { useLogout, useMe } from '@/lib/useAuth'

const USER_NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/upload', label: 'Upload' },
  { to: '/history', label: 'History' },
]

const ADMIN_NAV_ITEMS = [{ to: '/admin', label: 'Admin' }]

export function AppLayout() {
  const { data: user } = useMe()
  const logout = useLogout()
  const isAdmin = user?.role === 'admin'
  const navItems = isAdmin ? ADMIN_NAV_ITEMS : USER_NAV_ITEMS

  return (
    <div className="min-h-screen bg-[var(--color-page)]">
      <header className="sticky top-0 z-20 border-b border-[var(--color-border)] bg-[var(--color-page)]/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center gap-6 px-6 py-3">
          <div className="text-lg font-semibold tracking-tight">
            Feedback<span className="text-blue-600">IQ</span>
          </div>
          <nav className="flex items-center gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  clsx(
                    'rounded-lg px-3 py-1.5 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-blue-600/10 text-blue-600'
                      : 'text-[var(--color-ink-secondary)] hover:bg-black/5 dark:hover:bg-white/10',
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="flex-1" />
          <NavLink
            to="/profile"
            aria-label="Profile"
            className={({ isActive }) =>
              clsx(
                'flex h-9 w-9 items-center justify-center rounded-lg border border-[var(--color-border)] text-base hover:bg-black/5 dark:hover:bg-white/10',
                isActive && 'bg-blue-600/10 text-blue-600',
              )
            }
          >
            👤
          </NavLink>
          <ThemeToggle />
          <button
            onClick={() => logout.mutate()}
            className="rounded-lg px-3 py-1.5 text-sm font-medium text-[var(--color-ink-secondary)] hover:bg-black/5 dark:hover:bg-white/10"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <Outlet />
      </main>

      <FeedbackDetailDrawer />
    </div>
  )
}
