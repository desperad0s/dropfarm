import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the token in every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Add response interceptor to handle token refresh
let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({resolve, reject});
        }).then(token => {
          originalRequest.headers['Authorization'] = 'Bearer ' + token;
          return api(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      return new Promise((resolve, reject) => {
        api.post('/refresh', {
          refresh_token: localStorage.getItem('refreshToken')
        }).then(({data}) => {
          localStorage.setItem('token', data.access_token);
          api.defaults.headers.common['Authorization'] = 'Bearer ' + data.access_token;
          originalRequest.headers['Authorization'] = 'Bearer ' + data.access_token;
          processQueue(null, data.access_token);
          resolve(api(originalRequest));
        }).catch((err) => {
          processQueue(err, null);
          reject(err);
        }).finally(() => {
          isRefreshing = false;
        });
      });
    }

    return Promise.reject(error);
  }
);

// Add logout function
const logout = async () => {
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
};

// Add functions for project settings and bot control
const getProjectSettings = async () => {
  const response = await api.get('/projects/settings');
  return response.data;
};

const updateProjectSettings = async (settings) => {
  const response = await api.post('/projects/settings', settings);
  return response.data;
};

const startBot = async () => {
  const response = await api.post('/bot/start');
  return response.data;
};

const stopBot = async () => {
  const response = await api.post('/bot/stop');
  return response.data;
};

const login = async (username: string, password: string) => {
  try {
    const response = await api.post('/login', { username, password });
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('refreshToken', response.data.refresh_token);
    }
    return response.data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

const register = async (username: string, email: string, password: string) => {
  try {
    const response = await api.post('/register', { username, email, password });
    return response.data;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

const verifyToken = async () => {
  try {
    const response = await api.get('/verify_token');
    return response.data;
  } catch (error) {
    console.error('Token verification error:', error);
    throw error;
  }
};

const startRecording = async (url: string = 'https://web.telegram.org/k/') => {  // Updated URL
  const response = await api.post('/bot/start_recording', { url });
  return response.data;
};

const stopRecording = async (routineName: string) => {
  const response = await api.post('/bot/stop_recording', { routine_name: routineName });
  return response.data;
};

const getRecordedRoutines = async () => {
  const response = await api.get('/bot/recorded_routines');
  return response.data.routines;
};

const deleteRecordedRoutine = async (routineName: string) => {
  const response = await api.delete(`/bot/delete_routine/${routineName}`);
  return response.data;
};

export { 
  api, 
  login, 
  logout, 
  register, 
  verifyToken, 
  startRecording, 
  stopRecording, 
  getRecordedRoutines, 
  deleteRecordedRoutine 
};