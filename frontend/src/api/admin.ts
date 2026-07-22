import { apiClient } from './client'
import type { DashboardData, Feedback, Upload, User } from './types'

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

export async function fetchUserUploads(userId: string) {
  const res = await apiClient.get<Upload[]>(`/admin/users/${userId}/uploads`)
  return res.data
}

export async function fetchUserFeedback(userId: string) {
  const res = await apiClient.get<Feedback[]>(`/admin/users/${userId}/feedback`, { params: { limit: 100 } })
  return res.data
}

export async function fetchFeedbackByIdAsAdmin(feedbackId: string) {
  const res = await apiClient.get<Feedback>(`/admin/feedback/${feedbackId}`)
  return res.data
}

export async function approveUser(userId: string) {
  const res = await apiClient.post<User>(`/admin/users/${userId}/approve`)
  return res.data
}

export async function rejectUser(userId: string) {
  const res = await apiClient.post<User>(`/admin/users/${userId}/reject`)
  return res.data
}

export async function deleteFeedbackAsAdmin(feedbackId: string) {
  await apiClient.delete(`/admin/feedback/${feedbackId}`)
}

export async function deleteUploadAsAdmin(uploadId: string) {
  await apiClient.delete(`/admin/uploads/${uploadId}`)
}
