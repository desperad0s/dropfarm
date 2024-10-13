import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"

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
    <div>
      <h2 className="text-2xl font-bold mb-4">Bot Status</h2>
      <div className="flex items-center justify-between">
        <span className={`text-lg font-semibold ${status ? 'text-green-500' : 'text-red-500'}`}>
          {status ? 'Running' : 'Stopped'}
        </span>
        <Switch checked={status} onCheckedChange={handleToggle} />
      </div>
    </div>
  )
}
