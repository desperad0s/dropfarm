import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',  // Ensure this matches your Flask server address
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
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        // Implement your token refresh logic here
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post('http://localhost:5000/api/refresh', { refresh_token: refreshToken });
        const { access_token } = response.data;
        localStorage.setItem('token', access_token);
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh fails, redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

// Add logout function
const logout = async () => {
  try {
    await api.post('/logout');
  } finally {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  }
};

export { api, logout };