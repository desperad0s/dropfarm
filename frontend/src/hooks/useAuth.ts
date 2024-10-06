import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/router'

interface User {
  id: number
  username: string
  email: string
}

export function useAuth() {
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const storedToken = localStorage.getItem('authToken')
    if (storedToken) {
      setToken(storedToken)
      fetchUser(storedToken)
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = useCallback(async (authToken: string) => {
    try {
      const response = await fetch('/api/user', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        logout()
      }
    } catch (error) {
      console.error('Error fetching user data:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })
      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('authToken', data.access_token)
        setToken(data.access_token)
        await fetchUser(data.access_token)
        router.push('/dashboard')
      } else {
        throw new Error('Login failed')
      }
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }, [fetchUser, router])

  const logout = useCallback(() => {
    localStorage.removeItem('authToken')
    setToken(null)
    setUser(null)
    router.push('/login')
  }, [router])

  return { token, user, loading, login, logout }
}