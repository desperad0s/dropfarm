import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

type Routine = {
  id: number
  name: string
  steps: string[]
}

type RoutinesListProps = {
  routines: Routine[]
  onAddRoutine: (routine: Omit<Routine, 'id'>) => void
  onEditRoutine: (routine: Routine) => void
}

export function RoutinesList({ routines, onAddRoutine, onEditRoutine }: RoutinesListProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingRoutine, setEditingRoutine] = useState<Routine | null>(null)
  const [routineName, setRoutineName] = useState('')
  const [routineSteps, setRoutineSteps] = useState('')

  const handleAddOrEditRoutine = () => {
    const steps = routineSteps.split('\n').filter(step => step.trim() !== '')
    if (editingRoutine) {
      onEditRoutine({ ...editingRoutine, name: routineName, steps })
    } else {
      onAddRoutine({ name: routineName, steps })
    }
    setIsDialogOpen(false)
    setEditingRoutine(null)
    setRoutineName('')
    setRoutineSteps('')
  }

  const openDialog = (routine?: Routine) => {
    if (routine) {
      setEditingRoutine(routine)
      setRoutineName(routine.name)
      setRoutineSteps(routine.steps.join('\n'))
    } else {
      setEditingRoutine(null)
      setRoutineName('')
      setRoutineSteps('')
    }
    setIsDialogOpen(true)
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
              <span>{routine.name}</span>
              <Button variant="outline" onClick={() => openDialog(routine)}>
                Edit
              </Button>
            </li>
          ))}
        </ul>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="mt-4" onClick={() => openDialog()}>Add Routine</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingRoutine ? 'Edit Routine' : 'Add Routine'}</DialogTitle>
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
                <Label htmlFor="routineSteps">Steps (one per line)</Label>
                <textarea
                  id="routineSteps"
                  className="w-full h-32 p-2 border rounded"
                  value={routineSteps}
                  onChange={(e) => setRoutineSteps(e.target.value)}
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