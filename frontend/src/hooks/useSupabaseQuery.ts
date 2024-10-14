import { useState, useEffect, useCallback } from 'react'
import { supabase } from '@/lib/supabaseClient'
import { useAuth } from '@/contexts/AuthContext'

export function useSupabaseQuery<T>(query: 'dashboard' | string, select?: string) {
  const [data, setData] = useState<T | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const { session } = useAuth()

  const fetchData = useCallback(async () => {
    if (!session) {
      setError(new Error('No active session'))
      setIsLoading(false)
      return
    }

    try {
      setIsLoading(true)
      let result;
      if (query === 'dashboard') {
        const [routines, activities, userStats] = await Promise.all([
          supabase.from('routines').select('*').eq('user_id', session.user.id),
          supabase.from('activities').select('*').eq('user_id', session.user.id).order('created_at', { ascending: false }).limit(10),
          supabase.from('user_stats').select('*').eq('user_id', session.user.id).single()
        ]);
        result = {
          routines: routines.data,
          activities: activities.data,
          userStats: userStats.data
        };
      } else {
        const { data, error } = await supabase.from(query).select(select || '*')
        if (error) throw error
        result = data;
      }
      setData(result as T)
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e : new Error('An error occurred'))
      console.error('Error fetching data:', e)
    } finally {
      setIsLoading(false)
    }
  }, [query, select, session])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const refetch = useCallback(() => {
    fetchData()
  }, [fetchData])

  return { data, isLoading, error, refetch }
}
