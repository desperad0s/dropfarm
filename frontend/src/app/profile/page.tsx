"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, CheckCircle2 } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { changePassword } from "@/lib/api"

export default function ProfilePage() {
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [status, setStatus] = useState<{ type: "success" | "error"; message: string } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus(null)
    if (password !== confirmPassword) {
      setStatus({ type: "error", message: "Passwords do not match" })
      return
    }
    try {
      await changePassword(password)
      setStatus({ type: "success", message: "Password updated successfully" })
    } catch (err) {
      setStatus({ type: "error", message: "Failed to update password" })
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">User Profile</h1>
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
          <CardDescription>Update your account password</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="password">New Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm New Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
            <Button type="submit">Update Password</Button>
          </form>
        </CardContent>
        <CardFooter>
          {status && (
            <Alert variant={status.type === "success" ? "default" : "destructive"}>
              {status.type === "success" ? (
                <CheckCircle2 className="h-4 w-4" />
              ) : (
                <AlertCircle className="h-4 w-4" />
              )}
              <AlertTitle>{status.type === "success" ? "Success" : "Error"}</AlertTitle>
              <AlertDescription>{status.message}</AlertDescription>
            </Alert>
          )}
        </CardFooter>
      </Card>
    </div>
  )
}