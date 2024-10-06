"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { getStatistics } from "@/lib/api"
import { ActivityLog } from "@/types"

export default function StatisticsPage() {
  const [statistics, setStatistics] = useState<any>(null)

  useEffect(() => {
    fetchStatistics()
  }, [])

  const fetchStatistics = async () => {
    try {
      const data = await getStatistics()
      setStatistics(data)
    } catch (error) {
      console.error("Failed to fetch statistics", error)
    }
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h1 className="text-3xl font-bold">Statistics</h1>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Total Earnings</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">${statistics?.totalEarnings.toFixed(2)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Active Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{statistics?.activeProjects}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Total Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{statistics?.totalProjects}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Activity Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {statistics?.activityLogs.map((log: ActivityLog) => (
              <li key={log.id} className="text-sm">
                {new Date(log.timestamp).toLocaleString()}: {log.action}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}