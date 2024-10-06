'use client';

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { getBotStatus, startBot, stopBot, getStatistics } from '@/lib/api';
import io from 'socket.io-client';

interface Stats {
  total_tasks_completed: number;
  total_rewards_earned: number;
  current_streak: number;
}

export default function Dashboard() {
  const [botStatus, setBotStatus] = useState('Stopped');
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const status = await getBotStatus();
        setBotStatus(status);
        const statistics = await getStatistics();
        setStats(statistics);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        setError('Failed to fetch data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 30000); // Update every 30 seconds

    return () => clearInterval(intervalId);
  }, []);

  useEffect(() => {
    const socket = io('http://localhost:5000');
    socket.on('statistics_update', (data: Stats) => {
      setStats(data);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const handleStartBot = async () => {
    setLoading(true);
    setError(null);
    try {
      await startBot('goats');
      setBotStatus('Running');
    } catch (error) {
      console.error('Failed to start bot:', error);
      setError('Failed to start bot. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStopBot = async () => {
    setLoading(true);
    setError(null);
    try {
      await stopBot('goats');
      setBotStatus('Stopped');
    } catch (error) {
      console.error('Failed to stop bot:', error);
      setError('Failed to stop bot. Please try again.');
    } finally {
      setLoading(false);
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
          {loading && <p>Loading...</p>}
          {error && <p className="text-red-500">{error}</p>}
          {!loading && !error && (
            <>
              <p className="mb-4">Bot Status: {botStatus}</p>
              <div className="flex space-x-4 mb-4">
                <Button onClick={handleStartBot} disabled={botStatus === 'Running' || loading}>
                  Start Bot
                </Button>
                <Button onClick={handleStopBot} disabled={botStatus === 'Stopped' || loading}>
                  Stop Bot
                </Button>
              </div>
              {stats && (
                <div>
                  <h3 className="font-bold">Statistics:</h3>
                  <p>Tasks Completed: {stats.total_tasks_completed}</p>
                  <p>Rewards Earned: {stats.total_rewards_earned}</p>
                  <p>Current Streak: {stats.current_streak}</p>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}