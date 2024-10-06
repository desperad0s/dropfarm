'use client';

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "./ui/button"
import { logout } from "@/lib/api"

export function Header() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('token')
    setIsLoggedIn(!!token)
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
      <h1 className="text-2xl font-bold">Dropfarm</h1>
      {isLoggedIn ? (
        <Button onClick={handleLogout}>Logout</Button>
      ) : (
        <Button onClick={handleLogin}>Login</Button>
      )}
    </header>
  )
}