'use client';

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Switch } from "@/components/ui/switch"
import { getBotStatus, startBot, stopBot, getProjectSettings, updateProjectSettings } from '@/lib/api';
import { Play, Pause, Save, RefreshCw } from "lucide-react" // Import icons
import { Spinner } from "@/components/ui/spinner"

interface ProjectSettings {
  id: string;
  name: string;
  enabled: boolean;
  interval: number;
  maxDailyRuns: number;
}

export default function SettingsPage() {
  const [botStatus, setBotStatus] = useState('Stopped');
  const [projects, setProjects] = useState<ProjectSettings[]>([]);
  const [originalProjects, setOriginalProjects] = useState<ProjectSettings[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const fetchedProjects = await getProjectSettings();
        setProjects(fetchedProjects);
        setOriginalProjects(fetchedProjects);
      } catch (error) {
        console.error('Failed to fetch project settings:', error);
      } finally {
        setIsLoading(false);
      }
    }
    fetchData();
  }, []);

  if (isLoading) {
    return <Spinner />;
  }

  if (projects.length === 0) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Settings</h1>
        <p>No projects found. Please create a project first.</p>
      </div>
    );
  }

  const handleStartBot = async () => {
    try {
      await startBot(0);  // Pass 0 as the projectId to start all bots
      setBotStatus('Running');
    } catch (error) {
      console.error('Failed to start bot:', error);
    }
  };

  const handleStopBot = async () => {
    try {
      await stopBot(0);  // Pass 0 as the projectId to stop all bots
      setBotStatus('Stopped');
    } catch (error) {
      console.error('Failed to stop bot:', error);
    }
  };

  const handleProjectSettingChange = (projectId: string, field: keyof ProjectSettings, value: any) => {
    const updatedProjects = projects.map(project => 
      project.id === projectId ? { ...project, [field]: value } : project
    );
    setProjects(updatedProjects);
  };

  const handleSaveSettings = async () => {
    try {
      for (const project of projects) {
        await updateProjectSettings(project.id, project);
      }
      setOriginalProjects(projects);
      alert('Settings saved successfully');
    } catch (error) {
      console.error('Failed to save settings:', error);
      alert('Failed to save settings');
    }
  };

  const handleResetSettings = () => {
    setProjects(originalProjects);
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
              <Play className="mr-2 h-4 w-4" /> Start All Bots
            </Button>
            <Button onClick={handleStopBot} disabled={botStatus === 'Stopped'} variant="secondary">
              <Pause className="mr-2 h-4 w-4" /> Stop All Bots
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
          {projects.length > 0 && (
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
          )}
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <div className="flex justify-between">
            <Button onClick={handleSaveSettings}>
              <Save className="mr-2 h-4 w-4" /> Save Settings
            </Button>
            <Button variant="secondary" onClick={handleResetSettings}>
              <RefreshCw className="mr-2 h-4 w-4" /> Reset Settings
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}