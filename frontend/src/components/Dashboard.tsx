'use client'

import { useAuth } from '@/contexts/AuthContext'
import { BotStatus } from '@/components/dashboard/BotStatus'
import { EarningsOverview } from '@/components/dashboard/EarningsOverview'
import { ActivityLog } from '@/components/dashboard/ActivityLog'
import { UserStats } from '@/components/dashboard/UserStats'
import { RoutinesList, RoutinesListProps } from '@/components/dashboard/RoutinesList'
import { useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { useToast } from "@/hooks/use-toast"
import { RefreshCw } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useSupabaseQuery } from '@/hooks/useSupabaseQuery'
import { api } from '@/utils/api'

interface DashboardData {
  routines: Array<{
    id: string;
    name: string;
    steps: any; // You might want to define a more specific type for steps
    tokens_per_run: number;
    created_at: string;
    updated_at: string;
  }>;
  activities: Array<{
    id: string;
    user_id: string;
    action_type: string;
    details: string;
    created_at: string;
  }>;
  userStats: {
    id: string;
    user_id: string;
    total_routine_runs: number;
    total_earnings: number;
    last_run_date: string | null;
    total_tokens_generated: number;
  };
}

export function Dashboard() {
  const { user } = useAuth()
  const { toast } = useToast()
  const [isRefreshing, setIsRefreshing] = useState(false)

  const { data: dashboardData, isLoading, error, refetch } = useSupabaseQuery<DashboardData>('dashboard')

  const refreshDashboardData = useCallback(async () => {
    setIsRefreshing(true)
    try {
      await refetch()
      toast({
        title: "Dashboard Refreshed",
        description: "The dashboard data has been updated.",
      })
    } catch (error) {
      console.error('Error refreshing dashboard data:', error)
      toast({
        title: "Error",
        description: "Failed to refresh dashboard data. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsRefreshing(false)
    }
  }, [refetch, toast])

  const handleAddRoutine = useCallback(async (routine: Omit<RoutinesListProps['routines'][0], 'id'>) => {
    try {
      await api.post('/routines', routine);
      refetch();
      toast({
        title: "Routine Added",
        description: "The new routine has been added successfully.",
      })
    } catch (error) {
      console.error('Error adding routine:', error)
      toast({
        title: "Error",
        description: "Failed to add routine. Please try again.",
        variant: "destructive",
      })
    }
  }, [refetch, toast])

  const handleEditRoutine = useCallback(async (routine: RoutinesListProps['routines'][0]) => {
    try {
      await api.put(`/routines/${routine.id}`, routine);
      refetch();
      toast({
        title: "Routine Updated",
        description: "The routine has been updated successfully.",
      })
    } catch (error) {
      console.error('Error editing routine:', error)
      toast({
        title: "Error",
        description: "Failed to update routine. Please try again.",
        variant: "destructive",
      })
    }
  }, [refetch, toast])

  const handleDeleteRoutine = useCallback(async (id: string) => {
    try {
      await api.delete(`/routines/${id}`);
      refetch();
      toast({
        title: "Routine Deleted",
        description: "The routine has been deleted successfully.",
      })
    } catch (error) {
      console.error('Error deleting routine:', error)
      toast({
        title: "Error",
        description: "Failed to delete routine. Please try again.",
        variant: "destructive",
      })
    }
  }, [refetch, toast])

  if (isLoading) return <div className="flex items-center justify-center h-screen">Loading...</div>
  if (error) return <div className="flex items-center justify-center h-screen">Error loading dashboard data</div>
  if (!dashboardData) return <div className="flex items-center justify-center h-screen">No dashboard data available</div>

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Button onClick={refreshDashboardData} className="flex items-center gap-2" disabled={isRefreshing}>
          {isRefreshing ? 'Refreshing...' : (
            <>
              <RefreshCw className="h-4 w-4" />
              Refresh Data
            </>
          )}
        </Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Bot Status</CardTitle>
          </CardHeader>
          <CardContent>
            <BotStatus initialStatus={false} onToggle={() => {}} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Earnings Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <EarningsOverview totalTokensGenerated={dashboardData?.userStats?.total_tokens_generated || 0} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>User Stats</CardTitle>
          </CardHeader>
          <CardContent>
            <UserStats 
              totalRoutineRuns={dashboardData?.userStats?.total_routine_runs || 0}
              lastRunDate={dashboardData?.userStats?.last_run_date || null}
              totalTokensGenerated={dashboardData?.userStats?.total_tokens_generated || 0}
            />
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Routines</CardTitle>
        </CardHeader>
        <CardContent>
          <RoutinesList 
            routines={dashboardData?.routines || []}
            onAddRoutine={handleAddRoutine}
            onEditRoutine={handleEditRoutine}
            onDeleteRoutine={handleDeleteRoutine}
            onTranslateToHeadless={async (name: string) => {
              console.log(`Translating routine ${name} to headless`);
              // Implement the translation logic here
            }}
          />
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Activity Log</CardTitle>
        </CardHeader>
        <CardContent>
          <ActivityLog activities={dashboardData?.activities || []} />
        </CardContent>
      </Card>
    </div>
  )
}
