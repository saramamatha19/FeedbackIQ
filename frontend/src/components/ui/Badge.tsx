import type { ReactNode } from 'react'

export function Badge({ color, children }: { color: string; children: ReactNode }) {
  return (
    <span
      className="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium"
      style={{ color, backgroundColor: `${color}1a` }}
    >
      {children}
    </span>
  )
}
