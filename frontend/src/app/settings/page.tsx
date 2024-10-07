'use client';

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { getProjectSettings, updateProjectSettings, startBot, stopBot } from '@/lib/api'
import { useToast } from "@/hooks/use-toast"

export default function SettingsPage() {
  const [settings, setSettings] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    setIsLoading(true)
    try {
      const data = await getProjectSettings()
      setSettings(data)
    } catch (error) {
      console.error('Failed to fetch settings:', error)
      toast({
        title: "Error",
        description: "Failed to fetch settings",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleUpdateSettings = async () => {
    setIsLoading(true)
    try {
      await updateProjectSettings(settings)
      toast({
        title: "Success",
        description: "Settings updated successfully",
      })
    } catch (error) {
      console.error('Failed to update settings:', error)
      toast({
        title: "Error",
        description: "Failed to update settings",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleStartBot = async () => {
    setIsLoading(true)
    try {
      await startBot()
      toast({
        title: "Success",
        description: "Bot started successfully",
      })
    } catch (error) {
      console.error('Failed to start bot:', error)
      toast({
        title: "Error",
        description: "Failed to start bot",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleStopBot = async () => {
    setIsLoading(true)
    try {
      await stopBot()
      toast({
        title: "Success",
        description: "Bot stopped successfully",
      })
    } catch (error) {
      console.error('Failed to stop bot:', error)
      toast({
        title: "Error",
        description: "Failed to stop bot",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (!settings) {
    return <div>Loading...</div>
  }

  return (
    <div className="container mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle>Project Settings</CardTitle>
          <CardDescription>Manage your project settings here</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label htmlFor="projectName" className="block text-sm font-medium text-gray-700">Project Name</label>
              <Input
                id="projectName"
                value={settings.projectName || ''}
                onChange={(e) => setSettings({ ...settings, projectName: e.target.value })}
                className="mt-1"
              />
            </div>
            {/* Add more settings fields as needed */}
          </div>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button onClick={handleUpdateSettings} disabled={isLoading}>
            Update Settings
          </Button>
          <div>
            <Button onClick={handleStartBot} disabled={isLoading} className="mr-2">
              Start Bot
            </Button>
            <Button onClick={handleStopBot} disabled={isLoading} variant="destructive">
              Stop Bot
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}