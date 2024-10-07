'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { api, logout } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { useToast } from "@/hooks/use-toast"
import { Toaster } from "@/components/ui/toaster"

export default function Home() {
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [botStatus, setBotStatus] = useState<string>('stopped')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [activeRoutines, setActiveRoutines] = useState<string[]>([])
  const router = useRouter()
  const { toast } = useToast()

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

  if (!dashboardData) {
    return <div>Loading...</div>
  }

  return (
    <main className="flex min-h-screen flex-col items-center space-y-6 p-24">
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

      <Toaster />
    </main>
  )
}