import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { API_BASE_URL } from '@/config';

export function useRecordingStatus(taskId: string | null) {
  const [status, setStatus] = useState<string>('in_progress');
  const [error, setError] = useState<string | null>(null);
  const { session } = useAuth();

  useEffect(() => {
    if (!taskId) return;

    const checkStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/recording-status/${taskId}`, {
          headers: {
            'Authorization': `Bearer ${session?.access_token}`,
          },
        });
        if (!response.ok) {
          throw new Error('Failed to fetch recording status');
        }
        const data = await response.json();
        setStatus(data.status);
        setError(null);

        if (data.status !== 'in_progress') {
          clearInterval(intervalId);
        }
      } catch (error) {
        console.error('Error checking recording status:', error);
        setError(error instanceof Error ? error.message : 'An error occurred');
        clearInterval(intervalId);
      }
    };

    const intervalId = setInterval(checkStatus, 5000); // Check every 5 seconds

    return () => clearInterval(intervalId);
  }, [taskId, session]);

  return { status, error };
}
