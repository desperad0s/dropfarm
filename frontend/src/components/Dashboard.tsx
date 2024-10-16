'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useDataFetching } from '@/hooks/useDataFetching'
import { BotStatus } from '@/components/dashboard/BotStatus'
import { EarningsOverview } from '@/components/dashboard/EarningsOverview'
import { ActivityLog } from '@/components/dashboard/ActivityLog'
import { UserStats } from '@/components/dashboard/UserStats'
import { RoutinesList } from '@/components/dashboard/RoutinesList'
import { useState, useEffect, useCallback } from 'react'
import { API_BASE_URL } from '@/config'
import { Button } from '@/components/ui/button'
import { useToast } from "@/hooks/use-toast"
import { RefreshCw } from "lucide-react"
import { Calibration } from '@/components/Calibration'
import { useRecordingStatus } from '@/hooks/useRecordingStatus'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

export function Dashboard() {
  const { user, session } = useAuth()
  const [botStatus, setBotStatus] = useState(false)
  const { toast } = useToast()
  const [currentRecordingTask, setCurrentRecordingTask] = useState<{ id: string, name: string } | null>(null)
  const [isRecording, setIsRecording] = useState(false);
  const [showCalibration, setShowCalibration] = useState(false);
  const { status: recordingStatus, error: recordingError } = useRecordingStatus(currentRecordingTask?.id || null);

  const fetchDashboardData = useCallback(async () => {
    if (!session || !session.access_token) {
      throw new Error('No active session');
    }
    console.log("Fetching dashboard data with token:", session.access_token);
    const response = await fetch(`${API_BASE_URL}/dashboard`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${session.access_token}`,
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });
    if (!response.ok) {
      const errorData = await response.json();
      console.error("Dashboard fetch error:", errorData);
      throw new Error('Failed to fetch dashboard data');
    }
    return response.json();
  }, [session]);

  const { data, isLoading, error, setData } = useDataFetching(fetchDashboardData)

  const refreshDashboardData = useCallback(async () => {
    try {
      const newData = await fetchDashboardData();
      setData(newData);
      toast({
        title: "Dashboard Refreshed",
        description: "The dashboard data has been updated.",
      });
    } catch (error) {
      console.error('Error refreshing dashboard data:', error);
      toast({
        title: "Error",
        description: "Failed to refresh dashboard data. Please try again.",
        variant: "destructive",
      });
    }
  }, [fetchDashboardData, setData, toast]);

  const handleRecordRoutine = useCallback(async (routineName: string, tokensPerRun: number) => {
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
      setCurrentRecordingTask({ id: data.task_id, name: routineName });
      setIsRecording(true);
      toast({
        title: "Recording Started",
        description: "A new window will open. Press 7 to start recording, 8 to stop.",
      })

      // Poll for recording completion
      const pollInterval = setInterval(async () => {
        const statusResponse = await fetch(`${API_BASE_URL}/api/recording-status/${data.task_id}`, {
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
          },
        });
        const statusData = await statusResponse.json();
        if (statusData.status === 'completed') {
          clearInterval(pollInterval);
          setIsRecording(false);
          setCurrentRecordingTask(null);
          refreshDashboardData();  // Refresh dashboard data after recording is completed
        }
      }, 5000);  // Poll every 5 seconds

    } catch (error) {
      console.error('Error starting recording:', error);
      toast({
        title: "Error",
        description: `Failed to start recording: ${error instanceof Error ? error.message : String(error)}`,
        variant: "destructive",
      })
    }
  }, [session, toast, refreshDashboardData]);

  const handleBotToggle = useCallback(async (status: boolean) => {
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
  }, [session]);

  const handleAddRoutine = useCallback(async (routine: Omit<{ id: string; name: string; steps: string[]; tokens_per_run: number }, 'id'>) => {
    try {
      const response = await fetch(`${API_BASE_URL}/routines`, {
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
        toast({
          title: "Success",
          description: "New routine added successfully",
        });
      } else {
        throw new Error('Failed to add routine');
      }
    } catch (error) {
      console.error('Error adding routine:', error);
      toast({
        title: "Error",
        description: `Failed to add routine: ${error instanceof Error ? error.message : String(error)}`,
        variant: "destructive",
      });
    }
  }, [session, fetchDashboardData, toast]);

  const handleEditRoutine = useCallback(async (routine: { id: string; name: string; steps: string[]; tokens_per_run: number }) => {
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
  }, [session, fetchDashboardData]);

  const handlePlaybackRoutine = useCallback(async (name: string, repeatIndefinitely: boolean) => {
    try {
      const response = await fetch(`${API_BASE_URL}/start_playback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ name, repeat_indefinitely: repeatIndefinitely }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to start playback');
      }
      const data = await response.json();
      console.log(data.message);
      toast({
        title: "Playback Started",
        description: "A new window will open. Please wait for the browser to load, then press 9 to start the playback.",
      })
    } catch (error) {
      console.error('Error starting playback:', error);
      toast({
        title: "Error",
        description: `Failed to start playback: ${error instanceof Error ? error.message : String(error)}`,
        variant: "destructive",
      })
    }
  }, [session, toast]);

  const handleTranslateToHeadless = useCallback(async (name: string) => {
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
  }, [session]);

  const handlePopulateTestData = useCallback(async () => {
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
  }, [session, fetchDashboardData]);

  const cancelRecording = useCallback(async () => {
    if (currentRecordingTask && session?.access_token) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/cancel_recording`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`,
          },
          body: JSON.stringify({ 
            task_id: currentRecordingTask.id, 
            routine_name: currentRecordingTask.name 
          }),
        });
        if (!response.ok) {
          throw new Error('Failed to cancel recording');
        }
        setIsRecording(false);
        setCurrentRecordingTask(null);
        toast({
          title: "Recording Cancelled",
          description: "The recording task has been cancelled.",
        })
      } catch (error) {
        console.error('Error cancelling recording:', error);
        toast({
          title: "Error",
          description: `Failed to cancel recording: ${error instanceof Error ? error.message : String(error)}`,
          variant: "destructive",
        })
      }
    }
  }, [currentRecordingTask, session, toast]);

  const handleDeleteRoutine = useCallback(async (routineId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/routines/${routineId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to delete routine');
      }
      // Refresh dashboard data after successful deletion
      fetchDashboardData();
    } catch (error) {
      console.error('Error deleting routine:', error);
      toast({
        title: "Error",
        description: `Failed to delete routine: ${error instanceof Error ? error.message : String(error)}`,
        variant: "destructive",
      });
    }
  }, [session, fetchDashboardData, toast]);

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isRecording) {
        e.preventDefault();
        e.returnValue = 'You have an ongoing recording. Are you sure you want to leave?';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isRecording]);

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  if (!data) return <div>No data available</div>

  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Button onClick={refreshDashboardData} className="flex items-center gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh Data
        </Button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <BotStatus initialStatus={botStatus} onToggle={handleBotToggle} />
        <EarningsOverview 
          totalEarnings={data.totalEarnings} 
          earningsHistory={data.earningsHistory}
          totalTokensGenerated={data.totalTokensGenerated}
        />
        <UserStats 
          totalRoutineRuns={data.totalRoutineRuns} 
          lastRunDate={data.lastRunDate}
          totalTokensGenerated={data.totalTokensGenerated}
        />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActivityLog activities={data.activities} />
        <RoutinesList
          routines={data.routines}
          onAddRoutine={handleAddRoutine}
          onEditRoutine={handleEditRoutine}
          onRecordRoutine={handleRecordRoutine}
          onPlaybackRoutine={handlePlaybackRoutine}
          onTranslateToHeadless={handleTranslateToHeadless}
          onDeleteRoutine={handleDeleteRoutine}
        />
      </div>
      <div className="flex gap-4">
        <Button onClick={handlePopulateTestData}>Populate Test Data</Button>
        <Dialog>
          <DialogTrigger asChild>
            <Button>Start Calibration</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Calibration</DialogTitle>
              <DialogDescription>
                Calibrate your browser for optimal performance.
              </DialogDescription>
            </DialogHeader>
            <Calibration onClose={() => {}} />
          </DialogContent>
        </Dialog>
      </div>
      {currentRecordingTask && (
        <div className="mt-4 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Recording Status</h3>
          <p>{recordingStatus}</p>
          {recordingError && <p className="text-red-500 mt-2">Error: {recordingError}</p>}
        </div>
      )}
    </div>
  )
}