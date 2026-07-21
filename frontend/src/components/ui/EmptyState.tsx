import type { ReactNode } from 'react'

export function EmptyState({
  icon = '📭',
  title,
  body,
  action,
}: {
  icon?: string
  title: string
  body?: string
  action?: ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 px-6 py-16 text-center">
      <div className="text-4xl">{icon}</div>
      <div className="text-base font-medium text-[var(--color-ink)]">{title}</div>
      {body && <div className="max-w-sm text-sm text-[var(--color-ink-muted)]">{body}</div>}
      {action && <div className="mt-3">{action}</div>}
    </div>
  )
}
