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
  const response = await api.post('/login', { username, password });
  localStorage.setItem('token', response.data.access_token);
  return response.data;
};

export const logout = async () => {
  localStorage.removeItem('token');
};

export const getProjects = async () => {
  try {
    const response = await api.get('/projects');
    return response.data;
  } catch (error) {
    console.error('Error fetching projects:', error);
    return []; // Return an empty array if there's an error
  }
};

export const startBot = async (projectId: number) => {
  const endpoint = projectId ? `/bot/start/${projectId}` : '/bot/start';
  const response = await api.post(endpoint);
  return response.data;
};

export const stopBot = async (projectId: number) => {
  const endpoint = projectId ? `/bot/stop/${projectId}` : '/bot/stop';
  const response = await api.post(endpoint);
  return response.data;
};

export const getDashboardData = async () => {
  const response = await api.get('/dashboard');
  return response.data;
};

export const getEarningsData = async () => {
  const response = await api.get('/earnings');
  return response.data;
};

export const getBotStatus = async () => {
  const response = await api.get('/bot/status');
  return response.data.status;
};

export const getActivityLogs = async () => {
  const response = await api.get('/logs');
  return response.data;
};

export const getProjectSettings = async () => {
  try {
    const response = await api.get('/projects/settings');
    return response.data || []; // Ensure it returns an array, even if empty
  } catch (error) {
    console.error('Error fetching project settings:', error);
    return []; // Return an empty array in case of error
  }
};

export const updateProjectSettings = async (projectId: string, settings: Partial<Project>) => {
  const response = await api.put(`/projects/${projectId}/settings`, settings);
  return response.data;
};

export const getStatistics = async () => {
  const response = await api.get('/statistics');
  return {
    ...response.data,
    activityLogs: [] // Add this line to provide an empty array if the backend doesn't return activity logs
  };
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