import { useState } from 'react'
import { Link } from 'react-router-dom'
import clsx from 'clsx'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useLogin } from '@/lib/useAuth'
import { apiErrorMessage } from '@/api/client'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<'user' | 'admin'>('user')
  const login = useLogin()

  return (
    <Card className="p-6">
      <div className="mb-5 grid grid-cols-2 gap-1 rounded-lg bg-black/5 p-1 dark:bg-white/10">
        {(['user', 'admin'] as const).map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => setRole(option)}
            className={clsx(
              'rounded-md py-1.5 text-sm font-medium capitalize transition-colors',
              role === option
                ? 'bg-[var(--color-surface)] text-blue-600 shadow-sm'
                : 'text-[var(--color-ink-secondary)]',
            )}
          >
            {option}
          </button>
        ))}
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault()
          login.mutate({ email, password, expectedRole: role })
        }}
        className="space-y-4"
      >
        <div>
          <label className="mb-1 block text-xs font-medium text-[var(--color-ink-secondary)]">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-2 text-sm outline-none focus:border-blue-500"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-[var(--color-ink-secondary)]">Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-2 text-sm outline-none focus:border-blue-500"
          />
        </div>
        {login.isError && (
          <p className="text-xs text-red-500">{apiErrorMessage(login.error, 'Login failed.')}</p>
        )}
        <Button type="submit" className="w-full" disabled={login.isPending}>
          {login.isPending ? 'Signing in…' : 'Sign in'}
        </Button>
      </form>
      <p className="mt-4 text-center text-xs text-[var(--color-ink-muted)]">
        No account?{' '}
        <Link to="/register" className="font-medium text-blue-600 hover:underline">
          Create one
        </Link>
      </p>
    </Card>
  )
}
