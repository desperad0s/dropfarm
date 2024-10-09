'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface BotStatus {
  status: string;
  earnings: number;
  timestamp: number;
}

export function BotStatus() {
  const [status, setStatus] = useState<BotStatus | null>(null);

  useEffect(() => {
    const eventSource = new EventSource('/api/bot-status-stream');

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStatus(data);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  if (!status) return <div>Loading...</div>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Bot Status</CardTitle>
        <CardDescription>Real-time bot information</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Status: {status.status}</p>
        <p>Earnings: ${status.earnings.toFixed(2)}</p>
        <p>Last Updated: {new Date(status.timestamp * 1000).toLocaleString()}</p>
      </CardContent>
    </Card>
  );
}