export function formatDate(iso: string): string {
  const date = new Date(iso)
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

export function formatDateTime(iso: string): string {
  const date = new Date(iso)
  return `${date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} · ${date.toLocaleTimeString(
    undefined,
    { hour: 'numeric', minute: '2-digit' },
  )}`
}

export function compactNumber(n: number): string {
  return new Intl.NumberFormat(undefined, { notation: 'compact', maximumFractionDigits: 1 }).format(n)
}

export function truncate(text: string, max = 80): string {
  if (text.length <= max) return text
  return `${text.slice(0, max - 1)}…`
}
