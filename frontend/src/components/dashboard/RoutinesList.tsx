import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useToast } from "@/hooks/use-toast"
import { API_BASE_URL } from '@/config'
import { useAuth } from '@/contexts/AuthContext'

type Routine = {
  id: string
  name: string
  steps: string[]
  tokens_per_run: number
}

type RoutinesListProps = {
  routines: Routine[]
  onAddRoutine: (routine: Omit<Routine, 'id'>) => void
  onEditRoutine: (routine: Routine) => void
  onRecordRoutine: (name: string, tokensPerRun: number) => void
  onPlaybackRoutine: (name: string, repeatIndefinitely: boolean) => void
  onTranslateToHeadless: (name: string) => void
  onDeleteRoutine: (id: string) => void
}

export function RoutinesList({ 
  routines, 
  onAddRoutine, 
  onEditRoutine, 
  onRecordRoutine, 
  onPlaybackRoutine, 
  onTranslateToHeadless,
  onDeleteRoutine
}: RoutinesListProps) {
  const [newRoutineName, setNewRoutineName] = useState('')
  const [newTokensPerRun, setNewTokensPerRun] = useState(0)
  const [activePlayback, setActivePlayback] = useState<string | null>(null)
  const { toast } = useToast()
  const { session } = useAuth()

  const handleAddRoutine = () => {
    if (newRoutineName && newTokensPerRun > 0) {
      onAddRoutine({ name: newRoutineName, steps: [], tokens_per_run: newTokensPerRun })
      setNewRoutineName('')
      setNewTokensPerRun(0)
    }
  }

  const handlePlaybackRoutine = async (name: string, repeatIndefinitely: boolean) => {
    try {
      const response = await fetch(`${API_BASE_URL}/start_playback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ name, repeat_indefinitely: repeatIndefinitely }),
      })
      if (!response.ok) {
        throw new Error('Failed to start playback')
      }
      const data = await response.json()
      setActivePlayback(data.task_id)
      onPlaybackRoutine(name, repeatIndefinitely)
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to start playback: ${error instanceof Error ? error.message : String(error)}`,
        variant: "destructive",
      })
    }
  }

  const handleStopPlayback = async () => {
    if (!activePlayback) return
    try {
      const response = await fetch(`${API_BASE_URL}/stop_playback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ task_id: activePlayback }),
      })
      if (!response.ok) {
        throw new Error('Failed to stop playback')
      }
      setActivePlayback(null)
      toast({
        title: "Playback Stopped",
        description: "The routine playback has been stopped.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to stop playback: ${error instanceof Error ? error.message : String(error)}`,
        variant: "destructive",
      })
    }
  }

  const handleDeleteRoutine = async (routineId: string, taskId?: string) => {
    try {
      const url = taskId 
        ? `${API_BASE_URL}/routines/${routineId}?task_id=${taskId}`
        : `${API_BASE_URL}/routines/${routineId}`;
      
      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
        },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete routine');
      }
      onDeleteRoutine(routineId);
      toast({
        title: "Success",
        description: taskId ? "Recording cancelled and routine deleted successfully" : "Routine deleted successfully",
      });
    } catch (error) {
      console.error('Error deleting routine:', error);
      toast({
        title: "Error",
        description: `Failed to delete routine: ${error instanceof Error ? error.message : String(error)}`,
        variant: "destructive",
      });
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Routines</h2>
      <ul>
        {routines.map((routine) => (
          <li key={routine.id} className="mb-2 p-2 border rounded">
            <span>{routine.name} - {routine.tokens_per_run} tokens per run</span>
            <div className="mt-2">
              <Button onClick={() => onRecordRoutine(routine.name, routine.tokens_per_run)} className="mr-2">Record</Button>
              <Button onClick={() => handlePlaybackRoutine(routine.name, false)} className="mr-2">Play Once</Button>
              <Button onClick={() => handlePlaybackRoutine(routine.name, true)} className="mr-2">Play Indefinitely</Button>
              {activePlayback && <Button onClick={handleStopPlayback} variant="destructive">Stop</Button>}
              <Button onClick={() => onTranslateToHeadless(routine.name)} className="mr-2">Translate to Headless</Button>
              <Button onClick={() => onEditRoutine(routine)} className="mr-2">Edit</Button>
              <Button onClick={() => handleDeleteRoutine(routine.id)} variant="destructive">Delete</Button>
            </div>
          </li>
        ))}
      </ul>
      <div className="mt-4">
        <input
          type="text"
          value={newRoutineName}
          onChange={(e) => setNewRoutineName(e.target.value)}
          placeholder="New routine name"
          className="mr-2 p-2 border rounded"
        />
        <input
          type="number"
          value={newTokensPerRun}
          onChange={(e) => setNewTokensPerRun(Number(e.target.value))}
          placeholder="Tokens per run"
          className="mr-2 p-2 border rounded"
        />
        <Button onClick={handleAddRoutine}>Add Routine</Button>
      </div>
    </div>
  )
}
