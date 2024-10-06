"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Bell } from "lucide-react"
import { getNotifications } from "@/lib/api"
import { Notification } from "@/types"

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([])

  useEffect(() => {
    fetchNotifications()
  }, [])

  const fetchNotifications = async () => {
    try {
      const notificationsData = await getNotifications()
      setNotifications(notificationsData)
    } catch (error) {
      console.error("Failed to fetch notifications", error)
    }
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <h1 className="text-3xl font-bold">Notifications</h1>
      <Card>
        <CardHeader>
          <CardTitle>Recent Notifications</CardTitle>
        </CardHeader>
        <CardContent>
          {notifications.map((notification) => (
            <div key={notification.id} className="flex items-center space-x-4 py-2">
              <Bell className="h-5 w-5" />
              <div>
                <p>{notification.message}</p>
                <p className="text-sm text-muted-foreground">
                  {new Date(notification.timestamp).toLocaleString()}
                </p>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}