"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { logout } from "@/lib/api"

export function AuthButton() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const router = useRouter()

  useEffect(() => {
    setIsLoggedIn(!!localStorage.getItem('token'))
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
    <Button onClick={isLoggedIn ? handleLogout : handleLogin}>
      {isLoggedIn ? 'Logout' : 'Login'}
    </Button>
  )
}