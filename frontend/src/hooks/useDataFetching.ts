import { useState, useEffect } from 'react'
import { api } from '@/utils/api'
import { AxiosError } from 'axios'

interface FetchResult<T> {
  data: T | null
  isLoading: boolean
  error: Error | null
}

export function useDataFetching<T>(url: string): FetchResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get<T>(url)
        setData(response.data)
      } catch (err) {
        const error = err as AxiosError
        setError(new Error(error.message))
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [url])

  return { data, isLoading, error }
}
