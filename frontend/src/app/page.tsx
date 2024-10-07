'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { api, logout, startRecording, stopRecording, getRecordedRoutines, deleteRecordedRoutine, refreshRecordedRoutines } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { useToast } from "@/hooks/use-toast"
import { Toaster } from "@/components/ui/toaster"
import { Input } from "@/components/ui/input"

export default function Home() {
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [botStatus, setBotStatus] = useState<string>('stopped')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [activeRoutines, setActiveRoutines] = useState<string[]>([])
  const router = useRouter()
  const { toast } = useToast()
  const [isRecording, setIsRecording] = useState(false)
  const [recordingRoutineName, setRecordingRoutineName] = useState('')
  const [recordedRoutines, setRecordedRoutines] = useState<string[]>([])

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    } else {
      fetchDashboardData();
      const interval = setInterval(checkBotStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [])

  useEffect(() => {
    fetchRecordedRoutines()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/dashboard')
      setDashboardData(response.data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      toast({
        title: "Error",
        description: "Failed to fetch dashboard data",
        variant: "destructive",
      })
    }
  }

  const fetchRecordedRoutines = async () => {
    try {
      const routines = await getRecordedRoutines()
      setRecordedRoutines(routines)
    } catch (error) {
      console.error('Failed to fetch recorded routines:', error)
      showNotification("Error", "Failed to fetch recorded routines", "destructive")
    }
  }

  const showNotification = (title: string, description: string, variant: "default" | "destructive" = "default") => {
    toast({ title, description, variant })
    // Also update recent activities
    setDashboardData(prev => ({
      ...prev,
      recentActivities: [{ action: title, result: description }, ...prev.recentActivities.slice(0, 4)]
    }))
  }

  const initializeBot = async () => {
    setIsLoading(true)
    showNotification("Bot Initialization", "Bot is initializing...")
    try {
      const response = await api.post('/bot/initialize')
      await checkBotStatus()
      showNotification("Bot Initialization", response.data.message, response.data.status === 'success' ? "default" : "destructive")
    } catch (error) {
      console.error('Failed to initialize bot:', error)
      showNotification("Error", "Failed to initialize bot", "destructive")
    } finally {
      setIsLoading(false)
    }
  }

  const toggleRoutine = async (routine: string, isActive: boolean) => {
    setIsLoading(true)
    showNotification("Routine Toggle", `${isActive ? 'Starting' : 'Stopping'} ${routine} routine...`)
    try {
      if (isActive) {
        await api.post(`/bot/start/${routine}`)
        showNotification("Routine Started", `${routine} routine started successfully`)
      } else {
        await api.post(`/bot/stop/${routine}`)
        showNotification("Routine Stopped", `${routine} routine stopped successfully`)
      }
      await checkBotStatus()
    } catch (error) {
      console.error(`Failed to toggle ${routine} routine:`, error)
      showNotification("Error", `Failed to toggle ${routine} routine`, "destructive")
    } finally {
      setIsLoading(false)
    }
  }

  const stopBot = async () => {
    setIsLoading(true)
    showNotification("Bot Stopping", "Stopping the bot...")
    try {
      await api.post('/bot/stop')
      await checkBotStatus()
      showNotification("Bot Stopped", "Bot stopped successfully")
    } catch (error) {
      console.error('Failed to stop bot:', error)
      showNotification("Error", "Failed to stop bot", "destructive")
    } finally {
      setIsLoading(false)
    }
  }

  const checkBotStatus = async () => {
    try {
      const response = await api.get('/bot/status')
      setBotStatus(response.data.status)
      setActiveRoutines(response.data.active_routines)
    } catch (error) {
      console.error('Failed to get bot status:', error)
    }
  }

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/logout');
    } catch (error) {
      console.error('Logout failed:', error);
      toast({
        title: "Error",
        description: "Failed to log out",
        variant: "destructive",
      })
    }
  };

  const startRecordedRoutine = async (routine: string) => {
    setIsLoading(true)
    showNotification("Recorded Routine", `Starting recorded routine: ${routine}...`)
    try {
      const response = await api.post(`/bot/start_recorded/${routine}`)
      showNotification("Recorded Routine", `${routine} routine completed`)
      await checkBotStatus()
    } catch (error) {
      console.error(`Failed to start recorded routine ${routine}:`, error)
      showNotification("Error", `Failed to start recorded routine ${routine}`, "destructive")
    } finally {
      setIsLoading(false)
    }
  }

  const handleStartRecording = async () => {
    try {
      const response = await startRecording('https://web.telegram.org/k/')  // Updated URL
      setIsRecording(true)
      showNotification("Recording", response.message)
    } catch (error) {
      console.error('Failed to start recording:', error)
      showNotification("Error", "Failed to start recording", "destructive")
    }
  }

  const handleStopRecording = async () => {
    if (!recordingRoutineName) {
      showNotification("Error", "Please enter a routine name", "destructive")
      return
    }
    try {
      const response = await stopRecording(recordingRoutineName)
      setIsRecording(false)
      setRecordingRoutineName('')
      showNotification("Recording", response.message)
    } catch (error) {
      console.error('Failed to stop recording:', error)
      showNotification("Error", "Failed to stop recording", "destructive")
    }
  }

  const handleDeleteRoutine = async (routineName: string) => {
    try {
      await deleteRecordedRoutine(routineName)
      showNotification("Success", `Routine ${routineName} deleted successfully`)
      fetchRecordedRoutines()
    } catch (error) {
      console.error('Failed to delete routine:', error)
      showNotification("Error", `Failed to delete routine ${routineName}`, "destructive")
    }
  }

  const handleRefreshRoutines = async () => {
    try {
      const routines = await refreshRecordedRoutines();
      setRecordedRoutines(routines);
      showNotification("Success", "Recorded routines refreshed successfully");
    } catch (error) {
      console.error('Failed to refresh recorded routines:', error);
      showNotification("Error", "Failed to refresh recorded routines", "destructive");
    }
  };

  if (!dashboardData) {
    return <div>Loading...</div>
  }

  return (
    <main className="flex min-h-screen flex-col items-center space-y-6">
      {/* Bot Control Card */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Bot Control</CardTitle>
          <CardDescription>Status: {botStatus}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col space-y-4">
            <div className="flex space-x-4">
              <Button 
                onClick={initializeBot} 
                disabled={isLoading || botStatus !== 'stopped'}
                variant="outline"
              >
                Initialize Bot
              </Button>
              <Button 
                onClick={stopBot} 
                disabled={isLoading || botStatus === 'stopped'}
                variant="destructive"
              >
                Stop Bot
              </Button>
            </div>
            <div className="flex flex-col space-y-2">
              <div className="flex items-center justify-between">
                <span>GOATS Routine</span>
                <Switch
                  checked={activeRoutines.includes('goats')}
                  onCheckedChange={(checked) => toggleRoutine('goats', checked)}
                  disabled={isLoading || botStatus === 'stopped'}
                />
              </div>
              <div className="flex items-center justify-between">
                <span>1Win Routine</span>
                <Switch
                  checked={activeRoutines.includes('onewin')}
                  onCheckedChange={(checked) => toggleRoutine('onewin', checked)}
                  disabled={isLoading || botStatus === 'stopped'}
                />
              </div>
              <div className="flex items-center justify-between">
                <span>PX Routine</span>
                <Switch
                  checked={activeRoutines.includes('px')}
                  onCheckedChange={(checked) => toggleRoutine('px', checked)}
                  disabled={isLoading || botStatus === 'stopped'}
                />
              </div>
            </div>
          </div>
        </CardContent>
        <CardFooter>
          <div>
            <h3 className="text-lg font-semibold mb-2">Active Routines:</h3>
            <ul className="list-disc list-inside">
              {activeRoutines.map(routine => (
                <li key={routine}>{routine}</li>
              ))}
            </ul>
          </div>
        </CardFooter>
      </Card>

      {/* Dashboard Cards */}
      <div className="w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Bot Status</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{dashboardData.botStatus}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Tasks Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{dashboardData.userStats.totalTasksCompleted}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Rewards Earned</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{dashboardData.userStats.totalRewardsEarned}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Current Streak</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{dashboardData.userStats.currentStreak}</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activities */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Recent Activities</CardTitle>
        </CardHeader>
        <CardContent>
          <ul>
            {dashboardData.recentActivities.map((activity: any, index: number) => (
              <li key={index}>{activity.action} - {activity.result}</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <div className="flex flex-col space-y-2">
        <h3 className="text-lg font-semibold">Recorded Routines:</h3>
        <Button 
          onClick={() => startRecordedRoutine('goats')} 
          disabled={isLoading || botStatus === 'stopped'}
        >
          Start Recorded GOATS Routine
        </Button>
        <Button 
          onClick={() => startRecordedRoutine('onewin')} 
          disabled={isLoading || botStatus === 'stopped'}
        >
          Start Recorded 1Win Routine
        </Button>
        <Button 
          onClick={() => startRecordedRoutine('px')} 
          disabled={isLoading || botStatus === 'stopped'}
        >
          Start Recorded PX Routine
        </Button>
      </div>

      {/* Recording Controls */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Record New Routine</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col space-y-4">
            {!isRecording ? (
              <Button onClick={handleStartRecording} disabled={isLoading}>
                Start Recording
              </Button>
            ) : (
              <>
                <Input
                  placeholder="Enter routine name"
                  value={recordingRoutineName}
                  onChange={(e) => setRecordingRoutineName(e.target.value)}
                />
                <Button onClick={handleStopRecording} disabled={isLoading}>
                  Stop Recording and Save
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Recorded Routines */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Recorded Routines</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-center mb-4">
            <Button onClick={handleRefreshRoutines}>
              Refresh Routines
            </Button>
          </div>
          {recordedRoutines.length > 0 ? (
            <ul className="space-y-2">
              {recordedRoutines.map((routine) => (
                <li key={routine} className="flex justify-between items-center">
                  <span>{routine}</span>
                  <div>
                    <Button 
                      onClick={() => startRecordedRoutine(routine)} 
                      disabled={isLoading || botStatus === 'stopped'}
                      className="mr-2"
                    >
                      Start
                    </Button>
                    <Button 
                      onClick={() => handleDeleteRoutine(routine)}
                      variant="destructive"
                    >
                      Delete
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p>No recorded routines available.</p>
          )}
        </CardContent>
      </Card>

      <Toaster />
    </main>
  )
}