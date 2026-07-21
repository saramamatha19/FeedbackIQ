import type { ReactNode } from 'react'
import { Card } from '@/components/ui/Card'

export function ChartCard({
  title,
  subtitle,
  children,
  action,
}: {
  title: string
  subtitle?: string
  children: ReactNode
  action?: ReactNode
}) {
  return (
    <Card className="flex min-h-[280px] flex-col p-5">
      <div className="mb-3 flex items-start justify-between">
        <div>
          <h3 className="text-sm font-semibold text-[var(--color-ink)]">{title}</h3>
          {subtitle && <p className="text-xs text-[var(--color-ink-muted)]">{subtitle}</p>}
        </div>
        {action}
      </div>
      <div className="flex-1">{children}</div>
    </Card>
  )
}

export function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-xs shadow-lg">
      {label && <div className="mb-1 font-medium text-[var(--color-ink)]">{label}</div>}
      {payload.map((entry: any, i: number) => (
        <div key={i} className="flex items-center gap-2 text-[var(--color-ink-secondary)]">
          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: entry.color || entry.fill }} />
          <span>
            {entry.name}: <span className="font-medium text-[var(--color-ink)]">{entry.value}</span>
          </span>
        </div>
      ))}
    </div>
  )
}
