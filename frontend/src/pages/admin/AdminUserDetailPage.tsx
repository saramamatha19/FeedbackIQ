import { Link, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { deleteUploadAsAdmin, fetchAllUsers, fetchUserFeedback, fetchUserUploads } from '@/api/admin'
import { apiErrorMessage } from '@/api/client'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { FeedbackTable } from '@/features/feedback/FeedbackTable'
import { formatDateTime } from '@/lib/formatters'

const STATUS_COLOR: Record<string, string> = {
  completed: 'text-green-600',
  processing: 'text-blue-600',
  pending: 'text-[var(--color-ink-muted)]',
  failed: 'text-red-500',
  partial: 'text-amber-500',
}

const SOURCE_LABEL: Record<string, string> = { single: 'Single', paste: 'Paste', csv: 'CSV', xlsx: 'Excel' }

export function AdminUserDetailPage() {
  const { userId } = useParams<{ userId: string }>()
  const queryClient = useQueryClient()

  const { data: users } = useQuery({ queryKey: ['admin-users'], queryFn: fetchAllUsers })
  const person = users?.find((u) => u.id === userId)

  const { data: uploads, isLoading: uploadsLoading } = useQuery({
    queryKey: ['admin-user-uploads', userId],
    queryFn: () => fetchUserUploads(userId as string),
    enabled: !!userId,
  })

  const deleteUpload = useMutation({
    mutationFn: deleteUploadAsAdmin,
    onSuccess: () => {
      toast.success('Upload deleted.')
      queryClient.invalidateQueries({ queryKey: ['admin-user-uploads', userId] })
      queryClient.invalidateQueries({ queryKey: ['admin-user-feedback', userId] })
    },
    onError: (err) => toast.error(apiErrorMessage(err, 'Could not delete upload.')),
  })

  return (
    <div className="space-y-6">
      <div>
        <Link to="/admin" className="text-xs font-medium text-blue-600 hover:underline">
          ← Back to Admin
        </Link>
        <h1 className="mt-1 text-xl font-semibold">{person?.full_name ?? person?.email ?? 'User'}</h1>
        {person && (
          <p className="text-sm text-[var(--color-ink-muted)]">
            {person.email} · {person.role} · joined {formatDateTime(person.created_at)}
          </p>
        )}
      </div>

      <Card className="p-5">
        <h2 className="mb-3 text-sm font-semibold">Uploads</h2>
        {uploadsLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        ) : !uploads || uploads.length === 0 ? (
          <EmptyState icon="🗂️" title="No uploads" body="This person hasn't uploaded any feedback yet." />
        ) : (
          <div className="max-h-60 overflow-y-auto">
            <table className="w-full text-left text-sm">
              <thead className="sticky top-0 bg-[var(--color-surface)]">
                <tr className="border-b border-[var(--color-border)] text-xs text-[var(--color-ink-muted)]">
                  <th className="py-2 pr-3 font-medium">Source</th>
                  <th className="py-2 pr-3 font-medium">Filename</th>
                  <th className="py-2 pr-3 font-medium">Items</th>
                  <th className="py-2 pr-3 font-medium">Status</th>
                  <th className="py-2 pr-3 font-medium">Created</th>
                  <th className="py-2 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {uploads.map((upload) => (
                  <tr key={upload.id} className="border-b border-[var(--color-border)] last:border-0">
                    <td className="py-2.5 pr-3">{SOURCE_LABEL[upload.source_type]}</td>
                    <td className="py-2.5 pr-3 text-[var(--color-ink-secondary)]">
                      {upload.original_filename ?? '—'}
                    </td>
                    <td className="py-2.5 pr-3 tabular-nums">{upload.total_rows}</td>
                    <td className={`py-2.5 pr-3 font-medium ${STATUS_COLOR[upload.status]}`}>{upload.status}</td>
                    <td className="py-2.5 pr-3 text-xs text-[var(--color-ink-muted)]">
                      {formatDateTime(upload.created_at)}
                    </td>
                    <td className="py-2.5">
                      <button
                        onClick={() => {
                          if (
                            window.confirm(
                              'Delete this entire uploaded dataset? All its feedback and analysis will be permanently removed.',
                            )
                          ) {
                            deleteUpload.mutate(upload.id)
                          }
                        }}
                        disabled={deleteUpload.isPending}
                        className="text-xs font-medium text-red-500 hover:underline disabled:opacity-50"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <FeedbackTable
        title="Feedback"
        queryKey={['admin-user-feedback', userId]}
        queryFn={() => fetchUserFeedback(userId as string)}
        feedbackScope="admin"
        showExport={false}
      />
    </div>
  )
}
