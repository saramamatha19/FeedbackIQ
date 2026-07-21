import { useMemo, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Button } from '@/components/ui/Button'
import { submitPasteFeedback } from '@/api/uploads'
import { apiErrorMessage } from '@/api/client'

function estimateItemCount(text: string): number {
  const blankLineSplit = text.split(/\n\s*\n/).filter((s) => s.trim())
  if (blankLineSplit.length > 1) return blankLineSplit.length
  const lineSplit = text.split('\n').filter((s) => s.trim())
  return Math.max(lineSplit.length, text.trim() ? 1 : 0)
}

export function BulkPasteForm({ onSubmitted }: { onSubmitted: (uploadId: string) => void }) {
  const [text, setText] = useState('')
  const estimate = useMemo(() => estimateItemCount(text), [text])

  const mutation = useMutation({
    mutationFn: submitPasteFeedback,
    onSuccess: (upload) => {
      toast.success(`Splitting and analyzing ${upload.total_rows} item(s)…`)
      setText('')
      onSubmitted(upload.id)
    },
    onError: (err) => toast.error(apiErrorMessage(err, 'Could not process pasted feedback.')),
  })

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        if (!text.trim()) return
        mutation.mutate(text.trim())
      }}
      className="space-y-3"
    >
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={'One item per line, or blank-line separated…\n"The export button crashes on Safari"\n"Love the new dashboard"'}
        rows={8}
        className="w-full resize-none rounded-xl border border-[var(--color-border)] bg-transparent p-3 text-sm outline-none focus:border-blue-500"
      />
      <div className="flex items-center justify-between">
        <span className="text-xs text-[var(--color-ink-muted)]">
          {text.trim() ? `Detected: ~${estimate} item(s)` : ''}
        </span>
        <Button type="submit" disabled={mutation.isPending || !text.trim()}>
          {mutation.isPending ? 'Submitting…' : 'Analyze All →'}
        </Button>
      </div>
    </form>
  )
}
