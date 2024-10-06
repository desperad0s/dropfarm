'use client';

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "./ui/button"
import { logout } from "@/lib/api"
import { useAuth } from "@/lib/auth"

export function Header() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const router = useRouter()
  const { getUser } = useAuth()

  useEffect(() => {
    const user = getUser()
    setIsLoggedIn(!!user)
  }, [])

  const handleLogout = async () => {
    await logout()
    setIsLoggedIn(false)
    router.push('/login')
  }

  const handleLogin = () => {
    router.push('/login')
  }

  return (
    <header className="flex items-center justify-between p-4 bg-background border-b">
      <Link href="/" className="text-2xl font-bold">Dropfarm</Link>
      <nav className="flex items-center space-x-4">
        {isLoggedIn && (
          <>
            <Link href="/dashboard" className="text-sm font-semibold">Dashboard</Link>
            <Link href="/projects" className="text-sm font-semibold">Projects</Link>
            <Link href="/settings" className="text-sm font-semibold">Settings</Link>
          </>
        )}
        {isLoggedIn ? (
          <Button onClick={handleLogout}>Logout</Button>
        ) : (
          <Button onClick={handleLogin}>Login</Button>
        )}
      </nav>
    </header>
  )
}