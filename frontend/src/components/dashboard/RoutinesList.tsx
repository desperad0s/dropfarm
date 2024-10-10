import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

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
  onRecordRoutine: (routineName: string) => void
  onPlaybackRoutine: (name: string, url: string) => void
  onTranslateToHeadless: (name: string) => void
}

export function RoutinesList({ 
  routines, 
  onAddRoutine, 
  onEditRoutine, 
  onRecordRoutine, 
  onPlaybackRoutine, 
  onTranslateToHeadless 
}: RoutinesListProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingRoutine, setEditingRoutine] = useState<Routine | null>(null)
  const [routineName, setRoutineName] = useState('')
  const [tokensPerRun, setTokensPerRun] = useState('')

  const handleAddOrEditRoutine = () => {
    if (editingRoutine) {
      onEditRoutine({ ...editingRoutine, name: routineName, tokens_per_run: parseInt(tokensPerRun) })
    } else {
      onAddRoutine({ name: routineName, steps: [], tokens_per_run: parseInt(tokensPerRun) })
    }
    setIsDialogOpen(false)
    setEditingRoutine(null)
    setRoutineName('')
    setTokensPerRun('')
  }

  const openDialog = (routine?: Routine) => {
    if (routine) {
      setEditingRoutine(routine)
      setRoutineName(routine.name)
      setTokensPerRun(routine.tokens_per_run.toString())
    } else {
      setEditingRoutine(null)
      setRoutineName('')
      setTokensPerRun('')
    }
    setIsDialogOpen(true)
  }

  const handlePlaybackRoutine = (name: string) => {
    const url = 'https://web.telegram.org/k/';
    onPlaybackRoutine(name, url)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Routines</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {routines.map((routine) => (
            <li key={routine.id} className="flex items-center justify-between">
              <span>{routine.name} (Tokens per run: {routine.tokens_per_run})</span>
              <div>
                <Button variant="outline" onClick={() => openDialog(routine)}>Edit</Button>
                <Button variant="outline" onClick={() => handlePlaybackRoutine(routine.name)}>Playback</Button>
                <Button variant="outline" onClick={() => onTranslateToHeadless(routine.name)}>Translate to Headless</Button>
              </div>
            </li>
          ))}
        </ul>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="mt-4" onClick={() => openDialog()}>Add New Routine</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingRoutine ? 'Edit Routine' : 'Add New Routine'}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="routineName">Routine Name</Label>
                <Input
                  id="routineName"
                  value={routineName}
                  onChange={(e) => setRoutineName(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="tokensPerRun">Tokens per Run</Label>
                <Input
                  id="tokensPerRun"
                  type="number"
                  value={tokensPerRun}
                  onChange={(e) => setTokensPerRun(e.target.value)}
                />
              </div>
              <Button onClick={handleAddOrEditRoutine}>
                {editingRoutine ? 'Save Changes' : 'Add Routine'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  )
}