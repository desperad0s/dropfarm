"use client"

import React from 'react';
import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Play, Pause } from "lucide-react"
import { getProjects, startBot, stopBot } from "@/lib/api"
import { Project } from "@/types"

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const projectsData = await getProjects()
      setProjects(projectsData)
    } catch (error) {
      console.error("Failed to fetch projects", error)
    }
  }

  const handleToggleBot = async (projectId: string, currentStatus: string) => {
    try {
      if (currentStatus === "active") {
        await stopBot(projectId)
      } else {
        await startBot(projectId)
      }
      fetchProjects()
    } catch (error) {
      console.error("Failed to toggle bot", error)
    }
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h1 className="text-3xl font-bold">Projects</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {projects.map((project) => (
          <Card key={project.id}>
            <CardHeader>
              <CardTitle>{project.name}</CardTitle>
              <CardDescription>{project.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <Badge variant={project.status === "active" ? "default" : "secondary"}>
                {project.status}
              </Badge>
              <p className="mt-2 font-semibold">Recent Earnings: ${project.earnings.toFixed(2)}</p>
            </CardContent>
            <CardFooter>
              <Button
                variant={project.status === "active" ? "destructive" : "default"}
                onClick={() => handleToggleBot(project.id, project.status)}
              >
                {project.status === "active" ? (
                  <>
                    <Pause className="mr-2 h-4 w-4" /> Stop Bot
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" /> Start Bot
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  )
}