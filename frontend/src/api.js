import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 120000,
});

export const checkHealth = () => api.get('/health');

export const sendChatMessage = (question, sessionId) =>
  api.post('/chat', { question, session_id: sessionId });

export const getHistory = (sessionId) =>
  api.get('/history', {
    params: sessionId ? { session_id: sessionId } : {},
  });

export const exportResults = (sql) =>
  api.get('/export', {
    params: { sql },
    responseType: 'blob',
  });

export default api;