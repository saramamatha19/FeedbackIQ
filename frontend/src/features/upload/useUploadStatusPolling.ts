import { useQuery } from '@tanstack/react-query'
import { fetchUploadStatus } from '@/api/uploads'

export function useUploadStatusPolling(uploadId: string | null) {
  return useQuery({
    queryKey: ['upload-status', uploadId],
    queryFn: () => fetchUploadStatus(uploadId as string),
    enabled: !!uploadId,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === 'completed' || status === 'failed' ? false : 1500
    },
  })
}
