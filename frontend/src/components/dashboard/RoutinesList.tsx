import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useToast } from "@/hooks/use-toast"

type Routine = {
  id: string
  name: string
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
  const { toast } = useToast()
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleAddRoutine = () => {
    if (newRoutineName && newTokensPerRun > 0) {
      onAddRoutine({ name: newRoutineName, tokens_per_run: newTokensPerRun })
      setNewRoutineName('')
      setNewTokensPerRun(0)
      setIsDialogOpen(false); // Close the dialog
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
                    <Button size="sm" onClick={() => onRecordRoutine(routine.name, routine.tokens_per_run)}>Record</Button>
                    <Button size="sm" onClick={() => onPlaybackRoutine(routine.name, false)}>Play Once</Button>
                    <Button size="sm" onClick={() => onPlaybackRoutine(routine.name, true)}>Play Indefinitely</Button>
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
