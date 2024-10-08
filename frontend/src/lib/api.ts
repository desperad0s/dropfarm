import axios, { AxiosError } from 'axios';

const logApiCall = (functionName: string, ...args: any[]) => {
  console.log(`API Call: ${functionName}`, ...args);
};

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

export const login = async (email: string, password: string) => {
  try {
    const response = await api.post('/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('flaskToken', response.data.access_token);
    }
    return response.data;
  } catch (error) {
    // ... (error handling)
  }
};

export const fetchDashboardData = async () => {
  const response = await api.get('/dashboard');
  return response.data;
};

export const logout = async () => {
  localStorage.removeItem('flaskToken');
  // You might want to make an API call to invalidate the token on the server side
};

export const initializeBot = async () => {
  const response = await api.post('/bot/initialize');
  return response.data;
};

export const toggleRoutine = async (routine: string, isActive: boolean) => {
  const response = await api.post(`/bot/${isActive ? 'start' : 'stop'}/${routine}`);
  return response.data;
};

export const stopBot = async () => {
  const response = await api.post('/bot/stop');
  return response.data;
};

export const checkBotStatus = async () => {
  const response = await api.get('/bot/status');
  return response.data;
};

export const startRecording = async (url: string) => {
  const response = await api.post('/bot/start_recording', { url });
  return response.data;
};

export const stopRecording = async (routineName: string) => {
  const response = await api.post('/bot/stop_recording', { routineName });
  return response.data;
};

export const getRecordedRoutines = async () => {
  try {
    const response = await api.get('/bot/recorded_routines');
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Error fetching recorded routines:', error.response?.data || error.message);
      if (error.response?.status === 401) {
        // Handle unauthorized error (e.g., redirect to login)
        throw new Error('Unauthorized: Please log in again');
      }
    }
    throw error;
  }
};

export const deleteRecordedRoutine = async (routineName: string) => {
  const response = await api.delete(`/bot/recorded_routines/${routineName}`);
  return response.data;
};

export const refreshRecordedRoutines = async () => {
  const response = await api.get('/bot/refresh_recorded_routines');
  return response.data;
};

export const startRecordedRoutine = async (routineName: string) => {
  const response = await api.post(`/bot/start_recorded/${routineName}`);
  return response.data;
};

// Add authentication token to Flask API calls
api.interceptors.request.use(async (config) => {
  const token = localStorage.getItem('flaskToken');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

export { api };

export const register = async (email: string, password: string) => {
  logApiCall('register', email);
  try {
    const response = await api.post('/register', { email, password });
    console.log('Registration response:', response.data);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Registration error:', error.response.data);
        throw new Error(error.response.data.message || 'Registration failed');
      } else if (error.request) {
        // The request was made but no response was received
        console.error('No response received:', error.request);
        throw new Error('No response from server. Please try again later.');
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error('Error setting up request:', error.message);
        throw new Error('An error occurred. Please try again.');
      }
    } else {
      console.error('Registration error:', error);
      throw new Error('An unexpected error occurred. Please try again.');
    }
  }
};