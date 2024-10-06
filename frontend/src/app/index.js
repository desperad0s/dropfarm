import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export default function Home() {
  const [projects, setProjects] = useState([]);
  const [botStatus, setBotStatus] = useState({});

  useEffect(() => {
    // Fetch projects and bot status
    // This is a placeholder, replace with actual API calls
    setProjects([
      { id: 1, name: 'GOATS', description: 'GOATS Airdrop Project' },
      { id: 2, name: '1Win', description: '1Win Airdrop Project' },
      { id: 3, name: 'PX', description: 'PX Airdrop Project' },
    ]);
    setBotStatus({
      1: false,
      2: false,
      3: false,
    });
  }, []);

  const toggleBot = (projectId) => {
    // This is a placeholder, replace with actual API calls
    setBotStatus(prev => ({
      ...prev,
      [projectId]: !prev[projectId]
    }));
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