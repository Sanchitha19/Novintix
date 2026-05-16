import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const login = async (username, password) => {
  const response = await api.post('/token', { username, password });
  return response.data;
};

export const sendQuery = async (query, userId, sessionId, token) => {
  const response = await api.post('/query', 
    { 
      user_id: userId,
      text: query,
      session_id: sessionId
    },
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
  return response.data;
};

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
