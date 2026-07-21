import { apiClient } from './client'
import type { User } from './types'

export async function register(data: { email: string; password: string; full_name?: string }) {
  const res = await apiClient.post<User>('/auth/register', data)
  return res.data
}

export async function login(data: { email: string; password: string }) {
  const res = await apiClient.post<User>('/auth/login', data)
  return res.data
}

export async function logout() {
  await apiClient.post('/auth/logout')
}

export async function fetchMe() {
  const res = await apiClient.get<User>('/auth/me')
  return res.data
}
