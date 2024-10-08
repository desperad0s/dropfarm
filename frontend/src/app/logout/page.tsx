"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { logout } from '@/lib/api'

export default function Logout() {
  const router = useRouter()

  useEffect(() => {
    const performLogout = async () => {
      await logout()
      router.push('/login')
    }
    performLogout()
  }, [router])

  return <div>Logging out...</div>
}