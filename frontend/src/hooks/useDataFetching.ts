import { useState, useEffect } from 'react'

type DataState<T> = {
  data: T | null
  isLoading: boolean
  error: Error | null
}

export function useDataFetching<T>(fetchFunction: () => Promise<T>, dependencies: any[] = []) {
  const [state, setState] = useState<DataState<T>>({
    data: null,
    isLoading: true,
    error: null,
  })

  useEffect(() => {
    const fetchData = async () => {
      try {
        setState(prevState => ({ ...prevState, isLoading: true }))
        const result = await fetchFunction()
        setState({ data: result, isLoading: false, error: null })
      } catch (error) {
        setState({ data: null, isLoading: false, error: error as Error })
      }
    }

    fetchData()
  }, dependencies)

  return state
}