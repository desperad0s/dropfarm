'use client';

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Switch } from "@/components/ui/switch"
import { getBotStatus, startBot, stopBot, getProjectSettings, updateProjectSettings } from '@/lib/api';

interface ProjectSettings {
  id: string;
  name: string;
  enabled: boolean;
  interval: number;
  maxDailyRuns: number;
}

export default function SettingsPage() {
  const [botStatus, setBotStatus] = useState('Stopped');
  const [projects, setProjects] = useState<ProjectSettings[]>([
    { id: 'goats', name: 'GOATS', enabled: false, interval: 60, maxDailyRuns: 10 },
    { id: '1win', name: '1Win', enabled: false, interval: 60, maxDailyRuns: 10 },
    { id: 'px', name: 'PX', enabled: false, interval: 60, maxDailyRuns: 10 },
  ]);

  useEffect(() => {
    const fetchBotStatus = async () => {
      try {
        const status = await getBotStatus();
        setBotStatus(status);
      } catch (error) {
        console.error('Failed to fetch bot status:', error);
      }
    };

    const fetchProjectSettings = async () => {
      try {
        const settings = await getProjectSettings();
        setProjects(settings);
      } catch (error) {
        console.error('Failed to fetch project settings:', error);
      }
    };

    fetchBotStatus();
    fetchProjectSettings();

    const intervalId = setInterval(fetchBotStatus, 5000);
    return () => clearInterval(intervalId);
  }, []);

  const handleStartBot = async () => {
    try {
      await startBot();
      setBotStatus('Running');
    } catch (error) {
      console.error('Failed to start bot:', error);
    }
  };

  const handleStopBot = async () => {
    try {
      await stopBot();
      setBotStatus('Stopped');
    } catch (error) {
      console.error('Failed to stop bot:', error);
    }
  };

  const handleProjectSettingChange = async (projectId: string, field: keyof ProjectSettings, value: any) => {
    const updatedProjects = projects.map(project => 
      project.id === projectId ? { ...project, [field]: value } : project
    );
    setProjects(updatedProjects);

    try {
      await updateProjectSettings(projectId, { [field]: value });
    } catch (error) {
      console.error('Failed to update project settings:', error);
    }
  };

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h1 className="text-3xl font-bold">Settings</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Global Bot Control</CardTitle>
          <CardDescription>Start or stop all bots</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="mb-4">Bot Status: {botStatus}</p>
          <div className="flex space-x-4">
            <Button onClick={handleStartBot} disabled={botStatus === 'Running'}>
              Start All Bots
            </Button>
            <Button onClick={handleStopBot} disabled={botStatus === 'Stopped'}>
              Stop All Bots
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Project Settings</CardTitle>
          <CardDescription>Configure settings for each project</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue={projects[0].id}>
            <TabsList>
              {projects.map(project => (
                <TabsTrigger key={project.id} value={project.id}>{project.name}</TabsTrigger>
              ))}
            </TabsList>
            {projects.map(project => (
              <TabsContent key={project.id} value={project.id}>
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id={`${project.id}-enabled`}
                      checked={project.enabled}
                      onCheckedChange={(checked) => handleProjectSettingChange(project.id, 'enabled', checked)}
                    />
                    <Label htmlFor={`${project.id}-enabled`}>Enable {project.name}</Label>
                  </div>
                  <div className="grid w-full max-w-sm items-center gap-1.5">
                    <Label htmlFor={`${project.id}-interval`}>Interval (minutes)</Label>
                    <Input
                      type="number"
                      id={`${project.id}-interval`}
                      value={project.interval}
                      onChange={(e) => handleProjectSettingChange(project.id, 'interval', parseInt(e.target.value))}
                    />
                  </div>
                  <div className="grid w-full max-w-sm items-center gap-1.5">
                    <Label htmlFor={`${project.id}-maxDailyRuns`}>Max Daily Runs</Label>
                    <Input
                      type="number"
                      id={`${project.id}-maxDailyRuns`}
                      value={project.maxDailyRuns}
                      onChange={(e) => handleProjectSettingChange(project.id, 'maxDailyRuns', parseInt(e.target.value))}
                    />
                  </div>
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}