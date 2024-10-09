import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';

const BotStatus: React.FC = () => {
  const [status, setStatus] = useState<string>('unknown');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeRoutines, setActiveRoutines] = useState<string[]>([]);

  const initializeBot = async () => {
    setIsLoading(true);
    try {
      await api.post('/bot/initialize');
      checkBotStatus();
    } catch (error) {
      console.error('Failed to initialize bot:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const startRoutine = async (routine: string) => {
    setIsLoading(true);
    try {
      await api.post(`/bot/start/${routine}`);
      setActiveRoutines([...activeRoutines, routine]);
      checkBotStatus();
    } catch (error) {
      console.error(`Failed to start ${routine} routine:`, error);
    } finally {
      setIsLoading(false);
    }
  };

  const stopBot = async () => {
    setIsLoading(true);
    try {
      await api.post('/bot/stop');
      setActiveRoutines([]);
      checkBotStatus();
    } catch (error) {
      console.error('Failed to stop bot:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const checkBotStatus = async () => {
    try {
      const response = await api.get('/bot/status');
      setStatus(response.data.status);
    } catch (error) {
      console.error('Failed to get bot status:', error);
    }
  };

  useEffect(() => {
    const interval = setInterval(checkBotStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Bot Status: {status}</h2>
      <div className="flex space-x-4 mb-4">
        <Button 
          onClick={initializeBot} 
          disabled={isLoading || status !== 'stopped'}
          className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
        >
          Initialize Bot
        </Button>
        <Button 
          onClick={stopBot} 
          disabled={isLoading || status === 'stopped'}
          className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
        >
          Stop Bot
        </Button>
      </div>
      <div className="flex space-x-4">
        <Button 
          onClick={() => startRoutine('goats')} 
          disabled={isLoading || status !== 'running' || activeRoutines.includes('goats')}
          className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"
        >
          Start GOATS
        </Button>
        <Button 
          onClick={() => startRoutine('onewin')} 
          disabled={isLoading || status !== 'running' || activeRoutines.includes('onewin')}
          className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"
        >
          Start 1Win
        </Button>
        <Button 
          onClick={() => startRoutine('px')} 
          disabled={isLoading || status !== 'running' || activeRoutines.includes('px')}
          className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"
        >
          Start PX
        </Button>
      </div>
      <div className="mt-4">
        <h3 className="text-xl font-bold">Active Routines:</h3>
        <ul>
          {activeRoutines.map(routine => (
            <li key={routine}>{routine}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default BotStatus;