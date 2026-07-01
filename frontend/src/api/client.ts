import axios, { AxiosError } from 'axios'
import { useAuthStore } from '@/stores/authStore'

const API_BASE = '/api/v1'

export const api = axios.create({ baseURL: API_BASE, headers: { 'Content-Type': 'application/json' } })

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err: AxiosError) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().logout()
    }
    return Promise.reject(err)
  }
)

export function getErrorMessage(err: unknown): string {
  if (err instanceof AxiosError && err.response?.data) {
    const data = err.response.data as any
    return data.error || data.message || err.message
  }
  if (err instanceof Error) return err.message
  return 'Lỗi không xác định'
}
