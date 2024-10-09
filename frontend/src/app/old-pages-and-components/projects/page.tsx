"use client"

import { useEffect, useState } from 'react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { useToast } from '@/hooks/use-toast'
import axios from 'axios'

interface Project {
  id: number
  name: string
  status: string
  earnings: number
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const { toast } = useToast()

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const response = await axios.get('/api/projects', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      setProjects(response.data)
    } catch (error) {
      console.error('Error fetching projects:', error)
      toast({
        title: 'Error',
        description: 'Failed to fetch projects. Please try again.',
        variant: 'destructive',
      })
    }
  }

  const handleStartStop = async (projectId: number, action: 'start' | 'stop') => {
    try {
      await axios.post(`/api/bot/${action}`, { project_id: projectId }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      toast({
        title: 'Success',
        description: `Bot ${action}ed successfully`,
      })
      fetchProjects()  // Refresh the project list
    } catch (error) {
      console.error(`Error ${action}ing bot:`, error)
      toast({
        title: 'Error',
        description: `Failed to ${action} bot. Please try again.`,
        variant: 'destructive',
      })
    }
  }

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-2xl font-bold mb-5">Projects</h1>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Earnings</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {projects.map((project) => (
            <TableRow key={project.id}>
              <TableCell>{project.name}</TableCell>
              <TableCell>{project.status}</TableCell>
              <TableCell>${project.earnings.toFixed(2)}</TableCell>
              <TableCell>
                {project.status === 'active' ? (
                  <Button onClick={() => handleStartStop(project.id, 'stop')}>Stop</Button>
                ) : (
                  <Button onClick={() => handleStartStop(project.id, 'start')}>Start</Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}