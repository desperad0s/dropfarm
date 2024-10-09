"use client"

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { getActivityLogs } from '@/lib/api';

interface Log {
  id: number;
  timestamp: string;
  message: string;
  level: string;
}

export default function ActivityLogs() {
  const [logs, setLogs] = useState<Log[]>([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const fetchedLogs = await getActivityLogs();
        setLogs(fetchedLogs);
      } catch (error) {
        console.error('Failed to fetch activity logs:', error);
      }
    };

    fetchLogs();
    // Set up an interval to fetch logs periodically
    const intervalId = setInterval(fetchLogs, 30000);

    // Clean up the interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <Card className="w-full max-w-4xl">
        <CardHeader>
          <CardTitle>Activity Logs</CardTitle>
          <CardDescription>Recent bot activities and events</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {logs.map((log) => (
              <li key={log.id} className={`p-2 rounded ${log.level === 'ERROR' ? 'bg-red-100' : 'bg-gray-100'}`}>
                <span className="font-bold">{new Date(log.timestamp).toLocaleString()}</span> - {log.message}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}