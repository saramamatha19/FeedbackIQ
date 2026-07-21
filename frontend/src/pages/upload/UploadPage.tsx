import { useState } from 'react'
import clsx from 'clsx'
import { Card } from '@/components/ui/Card'
import { SingleFeedbackForm } from '@/features/upload/SingleFeedbackForm'
import { BulkPasteForm } from '@/features/upload/BulkPasteForm'
import { CsvDropzone } from '@/features/upload/CsvDropzone'
import { ProcessingStepper } from '@/features/upload/ProcessingStepper'

const TABS = [
  { key: 'single', label: 'Single' },
  { key: 'paste', label: 'Paste Multiple' },
  { key: 'csv', label: 'CSV Upload' },
] as const

type TabKey = (typeof TABS)[number]['key']

export function UploadPage() {
  const [tab, setTab] = useState<TabKey>('single')
  const [activeUploadId, setActiveUploadId] = useState<string | null>(null)

  if (activeUploadId) {
    return (
      <div className="mx-auto max-w-2xl space-y-4">
        <h1 className="text-xl font-semibold">Add Feedback</h1>
        <ProcessingStepper uploadId={activeUploadId} onReset={() => setActiveUploadId(null)} />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-xl font-semibold">Add Feedback</h1>

      <div className="flex gap-1 rounded-lg border border-[var(--color-border)] p-1">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={clsx(
              'flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
              tab === t.key ? 'bg-blue-600 text-white' : 'text-[var(--color-ink-secondary)] hover:bg-black/5 dark:hover:bg-white/10',
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      <Card className="p-6">
        {tab === 'single' && <SingleFeedbackForm />}
        {tab === 'paste' && <BulkPasteForm onSubmitted={setActiveUploadId} />}
        {tab === 'csv' && <CsvDropzone onSubmitted={setActiveUploadId} />}
      </Card>
    </div>
  )
}
