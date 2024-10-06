"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { getActivityLogs } from "@/lib/api"
import { ActivityLog } from "@/types"

export default function ActivityLogsPage() {
  const [logs, setLogs] = useState<ActivityLog[]>([])

  useEffect(() => {
    fetchActivityLogs()
  }, [])

  const fetchActivityLogs = async () => {
    try {
      const logsData = await getActivityLogs()
      setLogs(logsData)
    } catch (error) {
      console.error("Failed to fetch activity logs", error)
    }
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h1 className="text-3xl font-bold">Activity Logs</h1>
      <Card>
        <CardHeader>
          <CardTitle>Recent Bot Activities</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Project</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Details</TableHead>
                <TableHead>Timestamp</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {logs.map((log, index) => (
                <TableRow key={index}>
                  <TableCell>{log.project_id}</TableCell>
                  <TableCell>{log.action}</TableCell>
                  <TableCell>{log.details}</TableCell>
                  <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}