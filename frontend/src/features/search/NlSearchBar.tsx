import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { AnimatePresence, motion } from 'framer-motion'
import { runNlQuery } from '@/api/feedback'
import { useUiStore } from '@/store/uiStore'
import { CATEGORY_ICONS, SENTIMENT_COLORS } from '@/lib/constants'
import { truncate } from '@/lib/formatters'

export function NlSearchBar() {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const openDrawer = useUiStore((s) => s.openFeedbackDrawer)

  const mutation = useMutation({
    mutationFn: runNlQuery,
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    mutation.mutate(query.trim())
    setOpen(true)
  }

  return (
    <div className="relative w-full max-w-md">
      <form onSubmit={handleSubmit} className="relative">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-ink-muted)]">
          🔍
        </span>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query && setOpen(true)}
          placeholder="Ask your data… e.g. urgent login bugs"
          className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]/70 py-2 pl-9 pr-3 text-sm outline-none backdrop-blur-xl placeholder:text-[var(--color-ink-muted)] focus:border-blue-500"
        />
      </form>

      <AnimatePresence>
        {open && (
          <>
            <div className="fixed inset-0 z-30" onClick={() => setOpen(false)} />
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.15 }}
              className="absolute left-0 right-0 z-40 mt-2 max-h-96 overflow-y-auto rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]/95 p-2 shadow-2xl backdrop-blur-xl"
            >
              {mutation.isPending && (
                <div className="px-3 py-4 text-sm text-[var(--color-ink-muted)]">Thinking…</div>
              )}
              {mutation.isError && (
                <div className="px-3 py-4 text-sm text-red-500">Couldn't run that query. Try again.</div>
              )}
              {mutation.data && mutation.data.results.length === 0 && (
                <div className="px-3 py-4 text-sm text-[var(--color-ink-muted)]">
                  No matches for "{query}" — try a broader query.
                </div>
              )}
              {mutation.data?.results.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    openDrawer(item.id)
                    setOpen(false)
                  }}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm hover:bg-black/5 dark:hover:bg-white/10"
                >
                  <span>{item.prediction ? CATEGORY_ICONS[item.prediction.category] ?? '📋' : '📋'}</span>
                  <span className="flex-1 truncate">{truncate(item.raw_text, 70)}</span>
                  {item.prediction && (
                    <span
                      className="h-2 w-2 shrink-0 rounded-full"
                      style={{ backgroundColor: SENTIMENT_COLORS[item.prediction.sentiment] }}
                    />
                  )}
                </button>
              ))}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
