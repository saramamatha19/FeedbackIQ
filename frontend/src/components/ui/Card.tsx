import type { ReactNode } from 'react'
import clsx from 'clsx'

export function Card({
  children,
  className,
  glass = false,
}: {
  children: ReactNode
  className?: string
  glass?: boolean
}) {
  return (
    <div
      className={clsx(
        'rounded-2xl border shadow-sm',
        glass
          ? 'border-white/20 bg-white/60 backdrop-blur-xl dark:border-white/10 dark:bg-white/5'
          : 'border-[var(--color-border)] bg-[var(--color-surface)]',
        className,
      )}
    >
      {children}
    </div>
  )
}
