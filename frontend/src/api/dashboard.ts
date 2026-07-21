import { apiClient } from './client'
import type { DashboardResponse } from './types'

export async function fetchDashboard(params: { upload_id?: string; refresh?: boolean }) {
  const res = await apiClient.get<DashboardResponse>('/dashboard', { params })
  return res.data
}
