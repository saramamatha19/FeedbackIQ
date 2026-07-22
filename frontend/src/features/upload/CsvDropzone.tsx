import { useRef, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { toast } from 'sonner'
import clsx from 'clsx'
import { Button } from '@/components/ui/Button'
import { submitCsvUpload } from '@/api/uploads'
import { apiErrorMessage } from '@/api/client'

const MAX_SIZE_BYTES = 5 * 1024 * 1024

export function CsvDropzone({ onSubmitted }: { onSubmitted: (uploadId: string) => void }) {
  const [file, setFile] = useState<File | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [shake, setShake] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const mutation = useMutation({
    mutationFn: submitCsvUpload,
    onSuccess: (upload) => {
      toast.success(`Analyzing ${upload.total_rows} rows…`)
      setFile(null)
      onSubmitted(upload.id)
    },
    onError: (err) => toast.error(apiErrorMessage(err, 'Could not process file.')),
  })

  function rejectWith(message: string) {
    setError(message)
    setShake(true)
    setTimeout(() => setShake(false), 400)
  }

  function validateAndSet(candidate: File) {
    const name = candidate.name.toLowerCase()
    if (!name.endsWith('.csv') && !name.endsWith('.xlsx')) {
      rejectWith('⚠ Only .csv or .xlsx files are supported.')
      return
    }
    if (candidate.size > MAX_SIZE_BYTES) {
      rejectWith('⚠ File exceeds the 5MB limit.')
      return
    }
    setError(null)
    setFile(candidate)
  }

  return (
    <div className="space-y-3">
      {!file ? (
        <motion.div
          animate={shake ? { x: [0, -8, 8, -6, 6, 0] } : {}}
          onDragOver={(e) => {
            e.preventDefault()
            setDragOver(true)
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragOver(false)
            const dropped = e.dataTransfer.files[0]
            if (dropped) validateAndSet(dropped)
          }}
          onClick={() => inputRef.current?.click()}
          className={clsx(
            'flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-6 py-12 text-center transition-colors',
            dragOver
              ? 'border-blue-500 bg-blue-500/10'
              : error
                ? 'border-red-400'
                : 'border-[var(--color-border)] hover:border-blue-400',
          )}
        >
          <div className="text-3xl">⬆️</div>
          <div className="text-sm font-medium">Drag & drop your .csv or .xlsx here, or click to browse</div>
          <div className="text-xs text-[var(--color-ink-muted)]">
            Must include a "feedback" text column · max 5MB
          </div>
          <input
            ref={inputRef}
            type="file"
            accept=".csv,.xlsx"
            className="hidden"
            onChange={(e) => {
              const selected = e.target.files?.[0]
              if (selected) validateAndSet(selected)
            }}
          />
        </motion.div>
      ) : (
        <div className="flex items-center justify-between rounded-xl border border-[var(--color-border)] px-4 py-3">
          <div className="flex items-center gap-2 text-sm">
            <span>📄</span>
            <span className="font-medium">{file.name}</span>
            <span className="text-xs text-[var(--color-ink-muted)]">{(file.size / 1024).toFixed(0)} KB</span>
          </div>
          <div className="flex items-center gap-2">
            <Button size="sm" disabled={mutation.isPending} onClick={() => mutation.mutate(file)}>
              {mutation.isPending ? 'Uploading…' : 'Analyze →'}
            </Button>
            <button onClick={() => setFile(null)} className="text-[var(--color-ink-muted)]">
              ✕
            </button>
          </div>
        </div>
      )}
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  )
}
