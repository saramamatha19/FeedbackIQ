import { useQuery } from '@tanstack/react-query'
import { fetchDashboard } from '@/api/dashboard'

export function useDashboardData(uploadId?: string) {
  return useQuery({
    queryKey: ['dashboard', uploadId ?? 'all-time'],
    queryFn: () => fetchDashboard({ upload_id: uploadId }),
  })
}
