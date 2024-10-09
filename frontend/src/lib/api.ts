import { createClient } from '@supabase/supabase-js'
import axios from 'axios';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api',
  withCredentials: true,
});

// Log all requests
api.interceptors.request.use(request => {
  console.log('Starting Request', request)
  return request
})

// Log all responses
api.interceptors.response.use(response => {
  console.log('Response:', response)
  return response
})

export const login = async (email: string, password: string) => {
  try {
    console.log("Attempting login with Supabase...");
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) {
      console.error("Supabase login error:", error);
      throw error;
    }
    console.log("Supabase login successful:", data);
    return data;
  } catch (error) {
    console.error('Login error:', error)
    throw error
  }
}

export const register = async (email: string, password: string) => {
  try {
    // Register with Supabase
    const { data: supabaseData, error: supabaseError } = await supabase.auth.signUp({ email, password })
    if (supabaseError) throw supabaseError

    // If Supabase registration is successful, register with Flask backend
    if (supabaseData.user) {
      const response = await api.post('/register', { email, password });
      return { ...supabaseData, ...response.data };
    }

    return supabaseData;
  } catch (error) {
    console.error('Registration error:', error)
    throw error
  }
}

export const logout = async () => {
  const { error } = await supabase.auth.signOut()
  if (error) throw error
}

// The rest of the API calls (bot operations, etc.) should use the Flask backend
export const fetchDashboardData = async () => {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error('No active session')
  
  const response = await api.get('/api/dashboard', {
    headers: {
      Authorization: `Bearer ${session.access_token}`
    }
  });
  return response.data;
};

export const initializeBot = async () => {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error('No active session')

  const response = await api.post('/api/bot/initialize', {}, {
    headers: {
      Authorization: `Bearer ${session.access_token}`
    }
  });
  return response.data;
};

export const startRoutine = async (routine: string) => {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error('No active session')

  const response = await api.post(`/api/bot/start/${routine}`, {}, {
    headers: {
      Authorization: `Bearer ${session.access_token}`
    }
  });
  return response.data;
};

export const stopRoutine = async (routine: string) => {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error('No active session')

  const response = await api.post(`/api/bot/stop/${routine}`, {}, {
    headers: {
      Authorization: `Bearer ${session.access_token}`
    }
  });
  return response.data;
};

export const stopBot = async () => {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error('No active session')

  const response = await api.post('/api/bot/stop', {}, {
    headers: {
      Authorization: `Bearer ${session.access_token}`
    }
  });
  return response.data;
};

export const getBotStatus = async () => {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error('No active session')

  const response = await api.get('/api/bot/status', {
    headers: {
      Authorization: `Bearer ${session.access_token}`
    }
  });
  return response.data;
};

// Add other API functions as needed, following the same pattern

export { api };
