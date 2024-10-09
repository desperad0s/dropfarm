import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type BotStatusProps = {
  initialStatus: boolean
  onToggle: (status: boolean) => void
}

export function BotStatus({ initialStatus, onToggle }: BotStatusProps) {
  const [status, setStatus] = useState(initialStatus)

  const handleToggle = () => {
    const newStatus = !status
    setStatus(newStatus)
    onToggle(newStatus)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Bot Status</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <span className={`text-lg font-semibold ${status ? 'text-green-500' : 'text-red-500'}`}>
            {status ? 'Running' : 'Stopped'}
          </span>
          <Button onClick={handleToggle}>
            {status ? 'Stop' : 'Start'}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}