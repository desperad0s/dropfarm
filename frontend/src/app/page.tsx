'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { api, logout, fetchDashboardData, initializeBot, startRoutine, stopRoutine, stopBot, getBotStatus } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { useToast } from "@/hooks/use-toast"
import { Toaster } from "@/components/ui/toaster"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

interface DashboardData {
  botStatus: string;
  userStats: {
    totalTasksCompleted: number;
    totalRewardsEarned: number;
    currentStreak: number;
  };
  recentActivities: Array<{ action: string; result: string }>;
}

export default function Home() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [botStatus, setBotStatus] = useState<string>('stopped')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [activeRoutines, setActiveRoutines] = useState<string[]>([])
  const router = useRouter()
  const { toast } = useToast()

  useEffect(() => {
    const token = localStorage.getItem('supabaseToken');
    if (!token) {
      console.log("No token found, redirecting to login");
      router.push('/login');
    } else {
      console.log("Token found, fetching dashboard data");
      fetchDashboardData();
      const interval = setInterval(checkBotStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [])

  const fetchDashboardData = async () => {
    try {
      console.log("Fetching dashboard data");
      const data = await fetchDashboardData()
      console.log("Dashboard data received:", data);
      setDashboardData(data)
      setBotStatus(data.botStatus)
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
    toast({ title, description, variant });
    setDashboardData((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        recentActivities: [{ action: title, result: description }, ...prev.recentActivities.slice(0, 4)]
      };
    });
  }

  const initializeBotHandler = async () => {
    setIsLoading(true)
    showNotification("Bot Initialization", "Bot is initializing...")
    try {
      const response = await initializeBot()
      await checkBotStatus()
      showNotification("Bot Initialization", response.message, response.status === 'success' ? "default" : "destructive")
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
        await startRoutine(routine)
        showNotification("Routine Started", `${routine} routine started successfully`)
      } else {
        await stopRoutine(routine)
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

  const stopBotHandler = async () => {
    setIsLoading(true)
    showNotification("Bot Stopping", "Stopping the bot...")
    try {
      await stopBot()
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
      const status = await getBotStatus()
      setBotStatus(status.status)
      setActiveRoutines(status.active_routines)
    } catch (error) {
      console.error('Failed to get bot status:', error)
    }
  }

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/login');
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
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="mr-4 hidden md:flex">
            <a className="mr-6 flex items-center space-x-2" href="/">
              <span className="hidden font-bold sm:inline-block">Dropfarm</span>
            </a>
            <nav className="flex items-center space-x-6 text-sm font-medium">
              <a className="transition-colors hover:text-foreground/80 text-foreground" href="/dashboard">Dashboard</a>
              <a className="transition-colors hover:text-foreground/80 text-foreground/60" href="/routines">Routines</a>
              <a className="transition-colors hover:text-foreground/80 text-foreground/60" href="/settings">Settings</a>
            </nav>
          </div>
          <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
            <div className="w-full flex-1 md:w-auto md:flex-none">
              <Button onClick={handleLogout}>Logout</Button>
            </div>
            <Avatar>
              <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
              <AvatarFallback>CN</AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>
      <main className="flex-1">
        {/* Your existing dashboard content */}
      </main>
    </div>
  )
}