import axios from 'axios'
import { Project, BotConfig, ActivityLog, Notification } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
})

export async function login(username: string, password: string) {
  const response = await api.post('/login', { username, password })
  return response.data
}

export async function logout() {
  const response = await api.post('/logout')
  return response.data
}

export async function getProjects(): Promise<Project[]> {
  const response = await api.get('/projects')
  return response.data
}

export async function startBot(projectId: string) {
  const response = await api.post(`/bot/start`, { project_id: projectId })
  return response.data
}

export async function stopBot(projectId: string) {
  const response = await api.post(`/bot/stop`, { project_id: projectId })
  return response.data
}

export async function getBotConfig(projectId: string): Promise<BotConfig> {
  const response = await api.get(`/bot/config`, { params: { project_id: projectId } })
  return response.data
}

export async function updateBotConfig(projectId: string, config: BotConfig) {
  const response = await api.post(`/bot/config`, { project_id: projectId, ...config })
  return response.data
}

export async function getActivityLogs(): Promise<ActivityLog[]> {
  const response = await api.get('/bot/activity')
  return response.data
}

export async function changePassword(newPassword: string) {
  const response = await api.post('/user/change-password', { new_password: newPassword })
  return response.data
}

export async function getNotifications(): Promise<Notification[]> {
  const response = await api.get('/notifications')
  return response.data
}