"use client"

import { useEffect, useState } from "react"
import { getStatistics } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"

interface Statistics {
  totalRuns: number;
  successRate: number;
  averageEarningsPerRun: number;
  totalEarnings: number;
  activityLogs: Array<{ id: number; timestamp: string; action: string }>;
}

export default function StatisticsPage() {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        const data = await getStatistics();
        setStatistics(data);
      } catch (error) {
        console.error('Error fetching statistics:', error);
        setError("An error occurred while fetching statistics.");
      }
    };

    fetchStatistics();
  }, []);

  if (error) {
    return <div className="flex items-center justify-center h-screen">{error}</div>;
  }

  if (!statistics) {
    return <Spinner />;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Statistics</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Total Runs</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{statistics.totalRuns}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{(statistics.successRate * 100).toFixed(2)}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Average Earnings Per Run</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">${statistics.averageEarningsPerRun.toFixed(2)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Total Earnings</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">${statistics.totalEarnings.toFixed(2)}</p>
          </CardContent>
        </Card>
      </div>
      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Activity Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {statistics.activityLogs.map((log) => (
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