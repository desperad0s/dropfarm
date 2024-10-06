'use client';

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { getBotStatus, startBot, stopBot } from '@/lib/api';

export default function Dashboard() {
  const [botStatus, setBotStatus] = useState('Stopped');

  useEffect(() => {
    const fetchBotStatus = async () => {
      try {
        const status = await getBotStatus();
        setBotStatus(status);
      } catch (error) {
        console.error('Failed to fetch bot status:', error);
      }
    };

    fetchBotStatus();
    // Set up an interval to fetch status periodically
    const intervalId = setInterval(fetchBotStatus, 5000);

    // Clean up the interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  const handleStartBot = async () => {
    try {
      await startBot();
      setBotStatus('Running');
    } catch (error) {
      console.error('Failed to start bot:', error);
    }
  };

  const handleStopBot = async () => {
    try {
      await stopBot();
      setBotStatus('Stopped');
    } catch (error) {
      console.error('Failed to stop bot:', error);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Bot Dashboard</CardTitle>
          <CardDescription>Control and monitor your bot</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="mb-4">Bot Status: {botStatus}</p>
          <div className="flex space-x-4">
            <Button onClick={handleStartBot} disabled={botStatus === 'Running'}>
              Start Bot
            </Button>
            <Button onClick={handleStopBot} disabled={botStatus === 'Stopped'}>
              Stop Bot
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}