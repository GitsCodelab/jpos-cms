import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.dispatchEvent(new Event('auth:logout'))
    }
    return Promise.reject(error)
  },
)

export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
  changePassword: (old_password, new_password) =>
    api.post('/auth/change-password', { old_password, new_password }),
  getActiveSessions: () => api.get('/auth/sessions'),
  revokeAllSessions: () => api.post('/auth/revoke-all-sessions'),
}

export const dbConnectionAPI = {
  list: (params) => api.get('/config/database-connections', { params }),
  get: (id) => api.get(`/config/database-connections/${id}`),
  create: (data) => api.post('/config/database-connections', data),
  update: (id, data) => api.put(`/config/database-connections/${id}`, data),
  delete: (id) => api.delete(`/config/database-connections/${id}`),
  test: (id) => api.post(`/config/database-connections/${id}/test`),
  activate: (id, is_active) =>
    api.post(`/config/database-connections/${id}/activate`, null, { params: { is_active } }),
}

export default api
