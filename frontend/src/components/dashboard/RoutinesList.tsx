import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useToast } from "@/hooks/use-toast"
import { API_BASE_URL } from '@/config'
import { useAuth } from '@/contexts/AuthContext'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

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
  const [playbackStates, setPlaybackStates] = useState<Record<string, { isPlaying: boolean, isIndefinite: boolean }>>({})
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
      if (playbackStates[name]?.isPlaying) {
        await handleStopPlayback(name)
        return
      }

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
      setPlaybackStates(prev => ({
        ...prev,
        [name]: { isPlaying: true, isIndefinite: repeatIndefinitely }
      }))
      onPlaybackRoutine(name, repeatIndefinitely)

      // Start polling for playback status
      pollPlaybackStatus(name)
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to start playback: ${error instanceof Error ? error.message : String(error)}`,
        variant: "destructive",
      })
    }
  }

  const pollPlaybackStatus = async (name: string) => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/playback_status/${name}`, {
          headers: {
            'Authorization': `Bearer ${session?.access_token}`,
          },
        })
        if (!response.ok) {
          throw new Error('Failed to fetch playback status')
        }
        const data = await response.json()
        if (data.status === 'completed' || data.status === 'stopped') {
          setPlaybackStates(prev => ({
            ...prev,
            [name]: { isPlaying: false, isIndefinite: false }
          }))
          clearInterval(intervalId)
        }
      } catch (error) {
        console.error('Error checking playback status:', error)
        clearInterval(intervalId)
      }
    }

    const intervalId = setInterval(checkStatus, 5000) // Check every 5 seconds
  }

  const handleStopPlayback = async (name: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/stop_playback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ name }),
      })
      if (!response.ok) {
        throw new Error('Failed to stop playback')
      }
      setPlaybackStates(prev => ({
        ...prev,
        [name]: { isPlaying: false, isIndefinite: false }
      }))
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
    <Card>
      <CardHeader>
        <CardTitle>Routines</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          <ul className="space-y-4">
            {routines.map((routine) => (
              <li key={routine.id} className="p-4 border rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold">{routine.name}</span>
                  <span className="text-sm text-gray-500">{routine.tokens_per_run} tokens per run</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button size="sm" onClick={() => onRecordRoutine(routine.name, routine.tokens_per_run)}>Record</Button>
                  <Button 
                    size="sm" 
                    onClick={() => handlePlaybackRoutine(routine.name, false)}
                    variant={playbackStates[routine.name]?.isPlaying && !playbackStates[routine.name]?.isIndefinite ? "destructive" : "default"}
                  >
                    {playbackStates[routine.name]?.isPlaying && !playbackStates[routine.name]?.isIndefinite ? "Stop" : "Play Once"}
                  </Button>
                  <Button 
                    size="sm" 
                    onClick={() => handlePlaybackRoutine(routine.name, true)}
                    variant={playbackStates[routine.name]?.isPlaying && playbackStates[routine.name]?.isIndefinite ? "destructive" : "default"}
                  >
                    {playbackStates[routine.name]?.isPlaying && playbackStates[routine.name]?.isIndefinite ? "Stop" : "Play Indefinitely"}
                  </Button>
                  <Button size="sm" onClick={() => onTranslateToHeadless(routine.name)}>Translate to Headless</Button>
                  <Button size="sm" onClick={() => onEditRoutine(routine)}>Edit</Button>
                  <Button size="sm" onClick={() => handleDeleteRoutine(routine.id)} variant="destructive">Delete</Button>
                </div>
              </li>
            ))}
          </ul>
        </ScrollArea>
        <Dialog>
          <DialogTrigger asChild>
            <Button className="mt-4">Add Routine</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Routine</DialogTitle>
              <DialogDescription>
                Enter the details for your new routine.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <Input
                type="text"
                value={newRoutineName}
                onChange={(e) => setNewRoutineName(e.target.value)}
                placeholder="Routine name"
              />
              <Input
                type="number"
                value={newTokensPerRun}
                onChange={(e) => setNewTokensPerRun(Number(e.target.value))}
                placeholder="Tokens per run"
              />
              <Button onClick={handleAddRoutine}>Add Routine</Button>
            </div>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  )
}
