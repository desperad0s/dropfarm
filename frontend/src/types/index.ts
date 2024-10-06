export interface Project {
  id: string
  name: string
  description: string
  status: 'active' | 'inactive'
  earnings: number
}

export interface BotConfig {
  username: string
  password: string
  interval: string
  maxActions: string
}

export interface ActivityLog {
  project_id: string
  action: string
  details: string
  timestamp: string
}

export interface Notification {
  id: number
  message: string
  timestamp: string
}