"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from 'next/link'
import { api } from '@/lib/api'
import { useToast } from "@/hooks/use-toast"

export default function LoginForm() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [loginError, setLoginError] = useState("")
  const router = useRouter()
  const { toast } = useToast()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError("");
    try {
      const response = await api.post('/login', { username, password });
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('refreshToken', response.data.refresh_token);
      router.push('/');
    } catch (error) {
      console.error('Login failed:', error);
      setLoginError("Login failed. Please check your credentials.");
      toast({
        title: "Error",
        description: "Login failed. Please check your credentials.",
        variant: "destructive",
      })
    }
  };

  return (
    <form className="space-y-6" onSubmit={handleLogin}>
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

      {loginError && <p className="text-destructive">{loginError}</p>}

      <div>
        <Button type="submit" className="w-full">
          Sign in
        </Button>
      </div>

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
    </form>
  )
}