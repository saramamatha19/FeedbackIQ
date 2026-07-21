import { apiClient } from './client'
import type { Upload, UploadStatus } from './types'

export async function submitSingleFeedback(text: string) {
  const res = await apiClient.post('/feedback/single', { text })
  return res.data
}

export async function submitPasteFeedback(rawText: string) {
  const res = await apiClient.post<Upload>('/feedback/paste', { raw_text: rawText })
  return res.data
}

export async function submitCsvUpload(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await apiClient.post<Upload>('/uploads/csv', formData)
  return res.data
}

export async function fetchUploadStatus(uploadId: string) {
  const res = await apiClient.get<UploadStatus>(`/uploads/${uploadId}/status`)
  return res.data
}

export async function fetchUpload(uploadId: string) {
  const res = await apiClient.get<Upload>(`/uploads/${uploadId}`)
  return res.data
}

export async function fetchUploads(limit = 50, offset = 0) {
  const res = await apiClient.get<Upload[]>('/uploads', { params: { limit, offset } })
  return res.data
}
