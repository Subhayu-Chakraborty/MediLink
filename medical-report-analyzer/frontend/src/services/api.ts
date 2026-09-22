/**
 * src/services/api.ts
 * Axios instance with JWT interceptor and 401 auto-logout.
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '',          // Vite proxy routes API calls to localhost:8000
  timeout: 300000,      // 5 minutes — Ollama CPU analysis can take a while
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('medreport_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// On 401 → clear storage and redirect to login
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('medreport_token')
      localStorage.removeItem('medreport_user')
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
