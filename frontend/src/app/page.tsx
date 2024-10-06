"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Play, Pause, TrendingUp, Activity, DollarSign } from "lucide-react"
import { EarningsChart } from "@/components/earnings-chart"
import { getProjects, startBot, stopBot } from "@/lib/api"
import { Project } from "@/types"

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [totalEarnings, setTotalEarnings] = useState(0)
  const [activeBots, setActiveBots] = useState(0)
  const [recentActivities, setRecentActivities] = useState(0)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const projectsData = await getProjects()
      setProjects(projectsData)
      setTotalEarnings(projectsData.reduce((sum, project) => sum + project.earnings, 0))
      setActiveBots(projectsData.filter(project => project.status === "active").length)
      // TODO: Fetch recent activities from the API
      setRecentActivities(24) // Placeholder value
    } catch (error) {
      console.error("Failed to fetch dashboard data", error)
    }
  }

  const handleStartAllBots = async () => {
    try {
      await Promise.all(projects.map(project => startBot(project.id)))
      fetchDashboardData()
    } catch (error) {
      console.error("Failed to start all bots", error)
    }
  }

  const handleStopAllBots = async () => {
    try {
      await Promise.all(projects.map(project => stopBot(project.id)))
      fetchDashboardData()
    } catch (error) {
      console.error("Failed to stop all bots", error)
    }
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Bots</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeBots}</div>
            <p className="text-xs text-muted-foreground">+2 from last week</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Earnings</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${totalEarnings.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">+$123.45 from last month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recent Activities</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{recentActivities}</div>
            <p className="text-xs text-muted-foreground">In the last 24 hours</p>
          </CardContent>
        </Card>
      </div>
      <div className="flex space-x-4">
        <Button onClick={handleStartAllBots}>
          <Play className="mr-2 h-4 w-4" /> Start All Bots
        </Button>
        <Button variant="secondary" onClick={handleStopAllBots}>
          <Pause className="mr-2 h-4 w-4" /> Stop All Bots
        </Button>
      </div>
      <Card className="col-span-4">
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