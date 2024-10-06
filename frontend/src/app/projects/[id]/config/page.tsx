"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, CheckCircle2 } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { getBotConfig, updateBotConfig } from "@/lib/api"
import { BotConfig } from "@/types"

export default function BotConfigPage() {
  const { id } = useParams()
  const [config, setConfig] = useState<BotConfig>({
    username: "",
    password: "",
    interval: "",
    maxActions: "",
  })
  const [status, setStatus] = useState<{ type: "success" | "error"; message: string } | null>(null)

  useEffect(() => {
    fetchBotConfig()
  }, [id])

  const fetchBotConfig = async () => {
    try {
      const configData = await getBotConfig(id as string)
      setConfig(configData)
    } catch (error) {
      console.error("Failed to fetch bot configuration", error)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setConfig({ ...config, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus(null)
    try {
      await updateBotConfig(id as string, config)
      setStatus({ type: "success", message: "Configuration updated successfully" })
    } catch (err) {
      setStatus({ type: "error", message: "Failed to update configuration" })
    }
  }

  return (
    <div className="container mx-auto p-4">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Bot Configuration</CardTitle>
          <CardDescription>Configure your bot settings for Project {id}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                name="username"
                value={config.username}
                onChange={handleChange}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={config.password}
                onChange={handleChange}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="interval">Action Interval (minutes)</Label>
              <Input
                id="interval"
                name="interval"
                type="number"
                value={config.interval}
                onChange={handleChange}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="maxActions">Max Actions per Day</Label>
              <Input
                id="maxActions"
                name="maxActions"
                type="number"
                value={config.maxActions}
                onChange={handleChange}
                required
              />
            </div>
            <Button type="submit">Save Configuration</Button>
          </form>
        </CardContent>
        <CardFooter>
          {status && (
            <Alert variant={status.type === "success" ? "default" : "destructive"}>
              {status.type === "success" ? (
                <CheckCircle2 className="h-4 w-4" />
              ) : (
                <AlertCircle className="h-4 w-4" />
              )}
              <AlertTitle>{status.type === "success" ? "Success" : "Error"}</AlertTitle>
              <AlertDescription>{status.message}</AlertDescription>
            </Alert>
          )}
        </CardFooter>
      </Card>
    </div>
  )
}