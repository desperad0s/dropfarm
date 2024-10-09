'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useDataFetching } from '@/hooks/useDataFetching'
import { BotStatus } from '@/components/dashboard/BotStatus'
import { EarningsOverview } from '@/components/dashboard/EarningsOverview'
import { ActivityLog } from '@/components/dashboard/ActivityLog'
import { UserStats } from '@/components/dashboard/UserStats'
import { RoutinesList } from '@/components/dashboard/RoutinesList'
import { useState } from 'react'
import { API_BASE_URL } from '@/config'

export default function Dashboard() {
  const { user, session } = useAuth()
  const [botStatus, setBotStatus] = useState(false)

  const fetchDashboardData = async () => {
    if (!session || !session.access_token) {
      throw new Error('No active session');
    }
    const response = await fetch(`${API_BASE_URL}/api/dashboard`, {
      headers: {
        'Authorization': `Bearer ${session.access_token}`,
      },
    });
    if (!response.ok) {
      throw new Error('Failed to fetch dashboard data');
    }
    return response.json();
  }

  const { data, isLoading, error } = useDataFetching(fetchDashboardData)

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  if (!data) return <div>No data available</div>

  const handleBotToggle = async (status: boolean) => {
    try {
      const response = await fetch('/api/bot/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      if (response.ok) {
        setBotStatus(status);
      } else {
        throw new Error('Failed to toggle bot status');
      }
    } catch (error) {
      console.error('Error toggling bot status:', error);
    }
  }

  const handleAddRoutine = async (routine: Omit<{ id: number; name: string; steps: string[] }, 'id'>) => {
    try {
      const response = await fetch('/api/routines', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(routine),
      });
      if (response.ok) {
        // Refresh dashboard data
        fetchDashboardData();
      } else {
        throw new Error('Failed to add routine');
      }
    } catch (error) {
      console.error('Error adding routine:', error);
    }
  }

  const handleEditRoutine = async (routine: { id: number; name: string; steps: string[] }) => {
    try {
      const response = await fetch(`/api/routines/${routine.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(routine),
      });
      if (response.ok) {
        // Refresh dashboard data
        fetchDashboardData();
      } else {
        throw new Error('Failed to edit routine');
      }
    } catch (error) {
      console.error('Error editing routine:', error);
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <BotStatus initialStatus={botStatus} onToggle={handleBotToggle} />
        <EarningsOverview totalEarnings={data.totalEarnings} earningsHistory={data.earningsHistory} />
        <ActivityLog activities={data.activities} />
        <UserStats totalRoutineRuns={data.totalRoutineRuns} lastRunDate={data.lastRunDate} />
        <RoutinesList
          routines={data.routines}
          onAddRoutine={handleAddRoutine}
          onEditRoutine={handleEditRoutine}
        />
      </div>
    </div>
  )
}