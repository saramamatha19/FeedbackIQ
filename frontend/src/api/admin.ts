import { apiClient } from './client'
import type { DashboardData, Upload, User } from './types'

export interface UsageStats {
  total_users: number
  total_uploads: number
  total_feedback: number
  avg_confidence: number | null
  avg_processing_time_ms: number | null
  needs_review_count: number
}

export async function fetchUsageStats() {
  const res = await apiClient.get<UsageStats>('/admin/usage')
  return res.data
}

export async function fetchAllUsers() {
  const res = await apiClient.get<User[]>('/admin/users')
  return res.data
}

export async function fetchAllUploads() {
  const res = await apiClient.get<Upload[]>('/admin/uploads')
  return res.data
}

export async function fetchAdminDashboard() {
  const res = await apiClient.get<{ data: DashboardData }>('/admin/dashboard')
  return res.data
}
