import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useToast } from "@/hooks/use-toast"
import { useAuth } from '@/contexts/AuthContext'
import { api } from '@/utils/api'
import { supabase } from '@/lib/supabaseClient'
import axios from 'axios'

type Routine = {
  id: string
  name: string
  tokens_per_run: number
}

export type RoutinesListProps = {
  routines: Routine[]
  onAddRoutine: (routine: Omit<Routine, 'id'>) => Promise<void>
  onEditRoutine: (routine: Routine) => Promise<void>
  onDeleteRoutine: (id: string) => Promise<void>
  onTranslateToHeadless: (name: string) => Promise<void>
}

export function RoutinesList({ 
  routines, 
  onAddRoutine, 
  onEditRoutine, 
  onDeleteRoutine,
  onTranslateToHeadless
}: RoutinesListProps) {
  const [newRoutineName, setNewRoutineName] = useState('')
  const [newTokensPerRun, setNewTokensPerRun] = useState(0)
  const { toast } = useToast()
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const { session } = useAuth();

  const handleAddRoutine = async () => {
    if (newRoutineName && newTokensPerRun > 0) {
      try {
        setIsDialogOpen(false); // Close the dialog immediately to prevent double submissions
        const response = await api.post('/routines', {
          name: newRoutineName,
          tokens_per_run: newTokensPerRun
        });
        onAddRoutine(response.data);
        setNewRoutineName('');
        setNewTokensPerRun(0);
        toast({
          title: "Routine Added",
          description: "The new routine has been added successfully.",
        });
      } catch (error) {
        console.error('Error adding routine:', error);
        if (axios.isAxiosError(error) && error.response) {
          console.error('Error response:', error.response.data);
          toast({
            title: "Error",
            description: error.response.data.error || "Failed to add routine. Please try again.",
            variant: "destructive",
          });
        } else {
          toast({
            title: "Error",
            description: "An unexpected error occurred. Please try again.",
            variant: "destructive",
          });
        }
      }
    }
  }

  const handleRecordRoutine = async (name: string, tokensPerRun: number) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        throw new Error('No active session');
      }
      await api.post('/record', { 
        name, 
        tokens_per_run: tokensPerRun
      });
      toast({
        title: "Recording Started",
        description: `Recording started for routine: ${name}`,
      });
    } catch (error) {
      console.error('Error starting recording:', error);
      toast({
        title: "Error",
        description: "Failed to start recording. Please try again.",
        variant: "destructive",
      });
    }
  }

  const handlePlaybackRoutine = async (name: string, repeatIndefinitely: boolean) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        throw new Error('No active session');
      }
      await api.post('/start_playback', { 
        name, 
        repeat_indefinitely: repeatIndefinitely,
        access_token: session.access_token,
        refresh_token: session.refresh_token
      });
      toast({
        title: "Playback Started",
        description: `Playback started for routine: ${name}`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start playback. Please try again.",
        variant: "destructive",
      });
    }
  }

  const handleDeleteRoutine = async (id: string) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        throw new Error('No active session');
      }
      await api.delete(`/routines/${id}`);
      onDeleteRoutine(id);
      toast({
        title: "Routine Deleted",
        description: "The routine has been deleted successfully.",
      });
    } catch (error) {
      console.error('Error deleting routine:', error);
      toast({
        title: "Error",
        description: "Failed to delete routine. Please try again.",
        variant: "destructive",
      });
    }
  }

  const handleEditRoutine = async (routine: RoutinesListProps['routines'][0]) => {
    try {
      await api.put(`/routines/${routine.id}`, routine);
      onEditRoutine(routine);
      toast({
        title: "Routine Updated",
        description: "The routine has been updated successfully.",
      });
    } catch (error) {
      console.error('Error updating routine:', error);
      toast({
        title: "Error",
        description: "Failed to update routine. Please try again.",
        variant: "destructive",
      });
    }
  }

  return (
    <div>
      <div className="max-h-[500px] overflow-y-auto mb-4">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Tokens per Run</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {routines.map((routine) => (
              <TableRow key={routine.id}>
                <TableCell>{routine.name}</TableCell>
                <TableCell>{routine.tokens_per_run}</TableCell>
                <TableCell>
                  <div className="flex space-x-2">
                    <Button size="sm" onClick={() => handleRecordRoutine(routine.name, routine.tokens_per_run)}>Record</Button>
                    <Button size="sm" onClick={() => handlePlaybackRoutine(routine.name, false)}>Play Once</Button>
                    <Button size="sm" onClick={() => handlePlaybackRoutine(routine.name, true)}>Play Indefinitely</Button>
                    <Button size="sm" onClick={() => onTranslateToHeadless(routine.name)}>Translate to Headless</Button>
                    <Button size="sm" onClick={() => onEditRoutine(routine)}>Edit</Button>
                    <Button size="sm" variant="destructive" onClick={() => onDeleteRoutine(routine.id)}>Delete</Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogTrigger asChild>
          <Button className="mt-4" onClick={() => setIsDialogOpen(true)}>Add Routine</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New Routine</DialogTitle>
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
    </div>
  )
}
