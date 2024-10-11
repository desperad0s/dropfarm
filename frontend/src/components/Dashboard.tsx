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
import { Button } from '@/components/ui/button'

export function Dashboard() {
  const { user, session } = useAuth()
  const [botStatus, setBotStatus] = useState(false)

  const fetchDashboardData = async () => {
    if (!session || !session.access_token) {
      throw new Error('No active session');
    }
    console.log("Fetching dashboard data with token:", session.access_token);
    const response = await fetch(`${API_BASE_URL}/api/dashboard`, {
      headers: {
        'Authorization': `Bearer ${session.access_token}`,
      },
    });
    if (!response.ok) {
      const errorData = await response.json();
      console.error("Dashboard fetch error:", errorData);
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
      const response = await fetch(`${API_BASE_URL}/api/bot/toggle`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
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

  const handleAddRoutine = async (routine: Omit<{ id: string; name: string; steps: string[]; tokens_per_run: number }, 'id'>) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/routines`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
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

  const handleEditRoutine = async (routine: { id: string; name: string; steps: string[]; tokens_per_run: number }) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/routines/${routine.id}`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
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

  const handleRecordRoutine = async (routineName: string, tokensPerRun: number) => {
    try {
      if (!session || !session.access_token) {
        throw new Error('No active session');
      }
      console.log("Sending record request:", { name: routineName, tokens_per_run: tokensPerRun });
      const response = await fetch(`${API_BASE_URL}/api/record`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({ name: routineName, tokens_per_run: tokensPerRun }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to start recording');
      }
      const data = await response.json();
      console.log(data.message);
      alert('Recording task started. A new window should open. Log in to Telegram, then press F8 to start recording. Press F9 to stop recording when finished.');
    } catch (error) {
      console.error('Error starting recording:', error);
      alert(`Error starting recording: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  const handlePlaybackRoutine = async (name: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/playback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ name }),
      });
      if (!response.ok) {
        throw new Error('Failed to start playback');
      }
      const data = await response.json();
      console.log(data.message);
      alert('Playback window opened. Please switch to the new browser window and press F10 to start the playback.');
    } catch (error) {
      console.error('Error starting playback:', error);
      alert(`Error starting playback: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  const handleTranslateToHeadless = async (name: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/translate_headless`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ name }),
      });
      if (!response.ok) {
        throw new Error('Failed to translate routine to headless');
      }
      const data = await response.json();
      console.log(data.message);
    } catch (error) {
      console.error('Error translating routine to headless:', error);
    }
  }

  const handlePopulateTestData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/populate_test_data`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to populate test data');
      }
      const data = await response.json();
      console.log('Test data populated:', data);
      // Refresh dashboard data after populating
      fetchDashboardData();
    } catch (error) {
      console.error('Error populating test data:', error);
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <BotStatus initialStatus={botStatus} onToggle={handleBotToggle} />
        <EarningsOverview 
          totalEarnings={data.totalEarnings} 
          earningsHistory={data.earningsHistory}
          totalTokensGenerated={data.totalTokensGenerated}
        />
        <ActivityLog activities={data.activities} />
        <UserStats 
          totalRoutineRuns={data.totalRoutineRuns} 
          lastRunDate={data.lastRunDate}
          totalTokensGenerated={data.totalTokensGenerated}
        />
        <RoutinesList
          routines={data.routines}
          onAddRoutine={handleAddRoutine}
          onEditRoutine={handleEditRoutine}
          onRecordRoutine={handleRecordRoutine}
          onPlaybackRoutine={handlePlaybackRoutine}
          onTranslateToHeadless={handleTranslateToHeadless}
        />
        <Button onClick={handlePopulateTestData}>Populate Test Data</Button>
      </div>
    </div>
  )
}