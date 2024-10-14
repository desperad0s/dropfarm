import axios from 'axios';
import { API_BASE_URL } from '@/config';
import { supabase } from '@/lib/supabaseClient';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers['Authorization'] = `Bearer ${session.access_token}`;
    if (session.refresh_token) {
      config.headers['Refresh-Token'] = session.refresh_token;
    }
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response && error.response.status === 401) {
      const { data, error: refreshError } = await supabase.auth.refreshSession();
      if (refreshError) {
        window.location.href = '/login';
      } else if (data.session) {
        const originalRequest = error.config;
        originalRequest.headers['Authorization'] = `Bearer ${data.session.access_token}`;
        if (data.session.refresh_token) {
          originalRequest.headers['Refresh-Token'] = data.session.refresh_token;
        }
        return axios(originalRequest);
      }
    }
    return Promise.reject(error);
  }
);
