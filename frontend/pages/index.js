import { useState, useEffect } from 'react'
import axios from 'axios'
import useSWR from 'swr'

const fetcher = url => axios.get(url).then(res => res.data)

export default function Home() {
  const [user, setUser] = useState(null)
  const { data: projects, error } = useSWR('/api/projects', fetcher)

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token')
    if (token) {
      axios.get('/api/user', { headers: { Authorization: `Bearer ${token}` } })
        .then(res => setUser(res.data))
        .catch(err => console.error(err))
    }
  }, [])

  const handleStartBot = async (projectId) => {
    try {
      await axios.post('/api/bot/start', { project_id: projectId })
      // Update UI to show bot is running
    } catch (error) {
      console.error('Failed to start bot:', error)
    }
  }

  if (!user) return <div>Please log in</div>
  if (error) return <div>Failed to load projects</div>
  if (!projects) return <div>Loading...</div>

  return (
    <div>
      <h1>Dropfarm Dashboard</h1>
      <div>
        {projects.map(project => (
          <div key={project.id}>
            <h2>{project.name}</h2>
            <p>{project.description}</p>
            <button onClick={() => handleStartBot(project.id)}>Start Bot</button>
          </div>
        ))}
      </div>
    </div>
  )
}