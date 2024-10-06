"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Play, Pause, Activity, DollarSign, CreditCard, Users } from "lucide-react"
import { EarningsChart } from "@/components/earnings-chart"
import { getDashboardData, startBot, stopBot } from "@/lib/api"
import { useRouter } from "next/navigation"
import { Spinner } from "@/components/ui/spinner"
import io from 'socket.io-client'

interface DashboardData {
  totalEarnings: number;
  lastMonthEarnings: number;
  activeProjects: number;
  runningBots: number;
}

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const data = await getDashboardData();
        setDashboardData(data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        if (error.response?.status === 401) {
          setError("Unauthorized. Please log in again.");
          router.push('/login');
        } else {
          setError("An error occurred while fetching data.");
        }
      }
    };

    fetchInitialData();

    const socket = io('http://localhost:5000');
    
    socket.on('dashboard_update', (data: DashboardData) => {
      setDashboardData(data);
    });

    return () => {
      socket.disconnect();
    };
  }, [router]);

  const handleStartAllBots = async () => {
    try {
      await startBot(0);
      // The dashboard data will be updated via Socket.IO
    } catch (error) {
      console.error('Error starting all bots:', error);
    }
  };

  const handleStopAllBots = async () => {
    try {
      await stopBot(0);
      // The dashboard data will be updated via Socket.IO
    } catch (error) {
      console.error('Error stopping all bots:', error);
    }
  };

  if (error) {
    return <div className="flex items-center justify-center h-screen">{error}</div>;
  }

  if (!dashboardData) {
    return <Spinner />;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Earnings</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${dashboardData.totalEarnings?.toFixed(2) || 'N/A'}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Last Month</CardTitle>
            <CreditCard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${dashboardData.lastMonthEarnings?.toFixed(2) || 'N/A'}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.activeProjects || 'N/A'}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Running Bots</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.runningBots || 'N/A'}</div>
          </CardContent>
        </Card>
      </div>
      <div className="flex space-x-4 mt-4">
        <Button onClick={handleStartAllBots}>
          <Play className="mr-2 h-4 w-4" /> Start All Bots
        </Button>
        <Button variant="secondary" onClick={handleStopAllBots}>
          <Pause className="mr-2 h-4 w-4" /> Stop All Bots
        </Button>
      </div>
      <Card className="col-span-4 mt-4">
        <CardHeader>
          <CardTitle>Earnings Overview</CardTitle>
          <CardDescription>Your earnings across all projects for the past week</CardDescription>
        </CardHeader>
        <CardContent className="pl-2">
          <EarningsChart />
        </CardContent>
      </Card>
    </div>
  )
}