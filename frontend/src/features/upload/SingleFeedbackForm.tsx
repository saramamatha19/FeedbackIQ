import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Button } from '@/components/ui/Button'
import { submitSingleFeedback } from '@/api/uploads'
import { apiErrorMessage } from '@/api/client'
import { useUiStore } from '@/store/uiStore'

export function SingleFeedbackForm() {
  const [text, setText] = useState('')
  const queryClient = useQueryClient()
  const openDrawer = useUiStore((s) => s.openFeedbackDrawer)

  const mutation = useMutation({
    mutationFn: submitSingleFeedback,
    onSuccess: (data) => {
      toast.success('Feedback analyzed.')
      setText('')
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['feedback-list'] })
      openDrawer(data.feedback.id)
    },
    onError: (err) => toast.error(apiErrorMessage(err, 'Could not analyze feedback.')),
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
        placeholder="Paste one piece of feedback…"
        rows={5}
        className="w-full resize-none rounded-xl border border-[var(--color-border)] bg-transparent p-3 text-sm outline-none focus:border-blue-500"
      />
      <div className="flex justify-end">
        <Button type="submit" disabled={mutation.isPending || !text.trim()}>
          {mutation.isPending ? 'Analyzing…' : 'Analyze →'}
        </Button>
      </div>
    </form>
  )
}
