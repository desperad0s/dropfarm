"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from '@/lib/auth'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from 'next/link'

export default function LoginPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()
  const { login } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    try {
      await login(username, password)
      router.push('/') // Redirect to the homepage after successful login
    } catch (err) {
      setError('Failed to log in')
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center py-12 sm:px-6 lg:px-8 bg-background">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-foreground">Sign in to your account</h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-card py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <Label htmlFor="username" className="text-foreground">Username</Label>
              <div className="mt-2">
                <Input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="bg-background text-foreground"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="password" className="text-foreground">Password</Label>
              <div className="mt-2">
                <Input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-background text-foreground"
                />
              </div>
            </div>

            {error && <p className="text-destructive">{error}</p>}

            <div>
              <Button type="submit" className="w-full">
                Sign in
              </Button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-muted" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-card px-2 text-muted-foreground">Or</span>
              </div>
            </div>

            <div className="mt-6">
              <Link href="/register" className="w-full inline-flex justify-center rounded-md bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground shadow-sm hover:bg-secondary/90">
                Create new account
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}