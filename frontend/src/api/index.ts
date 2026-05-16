import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const knowledgeApi = {
  list: (params: any) => api.get('/knowledge/', { params }),
  create: (data: any) => api.post('/knowledge/', data),
  get: (id: number) => api.get(`/knowledge/${id}`),
  update: (id: number, data: any) => api.put(`/knowledge/${id}`, data),
  delete: (id: number) => api.delete(`/knowledge/${id}`),
  categories: () => api.get('/knowledge/categories/list'),
}

export const chatApi = {
  send: (data: { session_id?: string; message: string; lang?: string }) => api.post('/chat/send', data),
  history: (sessionId: string) => api.get(`/chat/history/${sessionId}`),
}

export const amazonApi = {
  analyze: (data: { text: string }) => api.post('/amazon/analyze', data),
}

export const analyticsApi = {
  overview: () => api.get('/analytics/overview'),
  intents: () => api.get('/analytics/intents/distribution'),
  trends: (days = 7) => api.get('/analytics/trends/daily', { params: { days } }),
  hotQuestions: (limit = 10) => api.get('/analytics/hot/questions', { params: { limit } }),
  recentSessions: (limit = 20) => api.get('/analytics/sessions/recent', { params: { limit } }),
}

export const configApi = {
  getLLM: () => api.get('/config/llm'),
  updateLLM: (data: { llm_api_key: string; llm_base_url: string; llm_model: string }) => api.put('/config/llm', data),
}

export const storeApi = {
  getProfile: () => api.get('/store/profile'),
  updateProfile: (data: any) => api.put('/store/profile', data),
}
