import { login as apiLogin, logout as apiLogout } from './api'

interface User {
  id: string;
  username: string;
  // Add other user properties as needed
}

export function useAuth() {
  const login = apiLogin;
  const logout = apiLogout;

  const getUser = (): User | null => {
    const token = localStorage.getItem('token');
    if (!token) return null;
    // In a real app, you might want to decode the token to get user info
    // For now, we'll just return a dummy user object if a token exists
    return token ? { id: '1', username: 'exampleuser' } : null;
  };

  return { login, logout, getUser };
}