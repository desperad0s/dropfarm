'use client';
import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export default function Home() {
  const [projects, setProjects] = useState([]);
  const [botStatus, setBotStatus] = useState({});

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch('http://localhost:5000/api/projects', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
      const data = await response.json();
      setProjects(data);
      const status = {};
      data.forEach(project => {
        status[project.id] = false;
      });
      setBotStatus(status);
    }
  };

  const toggleBot = async (projectId) => {
    const token = localStorage.getItem('token');
    const action = botStatus[projectId] ? 'stop' : 'start';
    const response = await fetch(`http://localhost:5000/api/bot/${action}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ project_id: projectId })
    });
    if (response.ok) {
      setBotStatus(prev => ({
        ...prev,
        [projectId]: !prev[projectId]
      }));
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Dropfarm Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.map(project => (
          <Card key={project.id}>
            <CardHeader>
              <CardTitle>{project.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p>{project.description}</p>
              <Button 
                onClick={() => toggleBot(project.id)}
                className={botStatus[project.id] ? 'bg-red-500' : 'bg-green-500'}
              >
                {botStatus[project.id] ? 'Stop Bot' : 'Start Bot'}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}