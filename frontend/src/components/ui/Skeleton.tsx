import type { CSSProperties } from 'react'
import clsx from 'clsx'

export function Skeleton({ className, style }: { className?: string; style?: CSSProperties }) {
  return <div className={clsx('animate-pulse rounded-md bg-black/10 dark:bg-white/10', className)} style={style} />
}

export function ChartSkeleton() {
  return (
    <div className="flex h-48 items-end justify-between gap-2 px-2">
      {[40, 65, 30, 80, 50, 70, 45].map((h, i) => (
        <Skeleton key={i} className="w-full" style={{ height: `${h}%` }} />
      ))}
    </div>
  )
}
