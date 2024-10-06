import axios from 'axios'
import { Project, BotConfig, ActivityLog, Notification } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

export const login = async (username: string, password: string) => {
  try {
    const response = await api.post('/login', { username, password });
    localStorage.setItem('token', response.data.access_token);
    return response.data;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};

export const logout = async () => {
  localStorage.removeItem('token');
};

export const getProjects = async () => {
  const response = await api.get('/projects');
  return response.data;
};

export const startBot = async (botName: string) => {
  const response = await api.post('/bot/start', { bot_name: botName });
  return response.data;
};

export const stopBot = async (botName: string) => {
  const response = await api.post('/bot/stop', { bot_name: botName });
  return response.data;
};

export const getBotStatus = async () => {
  const response = await api.get('/bot/status');
  return response.data.status;
};

export const getDashboardData = async () => {
  const response = await api.get('/dashboard');
  return response.data;
};

export const getEarningsData = async () => {
  const response = await api.get('/earnings');
  return response.data;
};

export const getActivityLogs = async () => {
  const response = await api.get('/logs');
  return response.data;
};

export const getProjectSettings = async () => {
  const response = await api.get('/projects/settings');
  return response.data || [];
};

export const updateProjectSettings = async (projectId: string, settings: Partial<Project>) => {
  const response = await api.put(`/projects/${projectId}/settings`, settings);
  return response.data;
};

export const getStatistics = async () => {
  const response = await api.get('/statistics');
  return response.data;
};

export const getSettings = async () => {
  const response = await api.get('/settings');
  return response.data;
};

export const updateSettings = async (settings: any) => {
  const response = await api.put('/settings', settings);
  return response.data;
};

export const register = async (username: string, password: string) => {
  const response = await api.post('/register', { username, password });
  return response.data;
};

export default api;