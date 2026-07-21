import { apiClient } from './client'
import type { Feedback, NLQueryResponse, Prediction } from './types'

export async function fetchFeedback(params: { upload_id?: string; limit?: number; offset?: number }) {
  const res = await apiClient.get<Feedback[]>('/feedback', { params })
  return res.data
}

export async function fetchFeedbackById(feedbackId: string) {
  const res = await apiClient.get<Feedback>(`/feedback/${feedbackId}`)
  return res.data
}

export async function rerunFeedback(feedbackId: string) {
  const res = await apiClient.post<Prediction>(`/feedback/${feedbackId}/rerun`)
  return res.data
}

export async function fetchPredictionHistory(feedbackId: string) {
  const res = await apiClient.get<Prediction[]>(`/feedback/${feedbackId}/predictions/history`)
  return res.data
}

export async function runNlQuery(query: string) {
  const res = await apiClient.post<NLQueryResponse>('/query/nl', { query })
  return res.data
}

export function exportFeedbackCsvUrl(uploadId?: string) {
  const base = `${apiClient.defaults.baseURL}/exports/feedback.csv`
  return uploadId ? `${base}?upload_id=${uploadId}` : base
}
