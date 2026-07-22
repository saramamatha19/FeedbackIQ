import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useRegister } from '@/lib/useAuth'
import { apiErrorMessage } from '@/api/client'

export function RegisterPage() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const register = useRegister()

  if (register.isSuccess) {
    return (
      <Card className="p-6 text-center">
        <div className="text-3xl">✅</div>
        <h2 className="mt-3 text-sm font-semibold">Account created</h2>
        <p className="mt-1 text-xs text-[var(--color-ink-muted)]">
          An admin needs to approve your account before you can sign in. Check back soon.
        </p>
        <Link to="/login" className="mt-4 inline-block text-xs font-medium text-blue-600 hover:underline">
          Back to sign in
        </Link>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <form
        onSubmit={(e) => {
          e.preventDefault()
          register.mutate({ email, password, full_name: fullName || undefined })
        }}
        className="space-y-4"
      >
        <div>
          <label className="mb-1 block text-xs font-medium text-[var(--color-ink-secondary)]">Full name</label>
          <input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-2 text-sm outline-none focus:border-blue-500"
          />
        </div>
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
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-2 text-sm outline-none focus:border-blue-500"
          />
        </div>
        {register.isError && (
          <p className="text-xs text-red-500">{apiErrorMessage(register.error, 'Registration failed.')}</p>
        )}
        <Button type="submit" className="w-full" disabled={register.isPending}>
          {register.isPending ? 'Creating account…' : 'Create account'}
        </Button>
      </form>
      <p className="mt-4 text-center text-xs text-[var(--color-ink-muted)]">
        Already have an account?{' '}
        <Link to="/login" className="font-medium text-blue-600 hover:underline">
          Sign in
        </Link>
      </p>
    </Card>
  )
}
