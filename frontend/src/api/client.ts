import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  withCredentials: true,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !window.location.pathname.startsWith('/login')) {
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export function apiErrorMessage(error: unknown, fallback = 'Something went wrong.'): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return 'Could not reach the server. Is the backend running?'
    }
    const detail = error.response.data?.detail
    if (typeof detail === 'string') return detail
    // FastAPI/Pydantic validation errors (422) come back as an array of
    // {loc, msg} objects rather than a plain string — surface the first one
    // instead of silently falling back to a generic message.
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0]
      const field = Array.isArray(first?.loc) ? first.loc[first.loc.length - 1] : null
      return field ? `${field}: ${first.msg}` : (first?.msg ?? fallback)
    }
  }
  if (error instanceof Error && error.message) return error.message
  return fallback
}
