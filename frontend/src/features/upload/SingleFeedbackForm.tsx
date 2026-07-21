import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Button } from '@/components/ui/Button'
import { submitSingleFeedback } from '@/api/uploads'
import { apiErrorMessage } from '@/api/client'
import { PredictionSummary } from '@/features/feedback/PredictionSummary'
import type { Prediction } from '@/api/types'

export function SingleFeedbackForm() {
  const [text, setText] = useState('')
  const [result, setResult] = useState<Prediction | null>(null)
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: submitSingleFeedback,
    onSuccess: (data) => {
      toast.success('Feedback analyzed.')
      setText('')
      setResult(data.prediction)
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['feedback-list'] })
    },
    onError: (err) => toast.error(apiErrorMessage(err, 'Could not analyze feedback.')),
  })

  return (
    <div className="space-y-5">
      <form
        onSubmit={(e) => {
          e.preventDefault()
          if (!text.trim()) return
          setResult(null)
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

      {result && (
        <div className="border-t border-[var(--color-border)] pt-5">
          <PredictionSummary prediction={result} />
        </div>
      )}
    </div>
  )
}
