'use client';

import React from 'react'
import Link from 'next/link'
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { logout } from "@/lib/api"

export function Header() {
  const router = useRouter()

  const handleLogout = async () => {
    try {
      await logout()
      router.push("/login")
    } catch (error) {
      console.error("Failed to logout", error)
    }
  }

  return (
    <header className="bg-white shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" aria-label="Top">
        <div className="w-full py-6 flex items-center justify-between border-b border-indigo-500 lg:border-none">
          <div className="flex items-center">
            <Link href="/">
              <span className="sr-only">Your Company</span>
              <img
                className="h-10 w-auto"
                src="/logo.png"
                alt="Your Company"
              />
            </Link>
            <div className="hidden ml-10 space-x-8 lg:block">
              <Link href="/settings" className="text-base font-medium text-gray-500 hover:text-gray-900">
                Settings
              </Link>
              <Link href="/activity-logs" className="text-base font-medium text-gray-500 hover:text-gray-900">
                Activity Logs
              </Link>
            </div>
          </div>
          <div className="ml-10 space-x-4">
            <Button onClick={handleLogout}>Logout</Button>
          </div>
        </div>
        <div className="py-4 flex flex-wrap justify-center space-x-6 lg:hidden">
          <Link href="/settings" className="text-base font-medium text-gray-500 hover:text-gray-900">
            Settings
          </Link>
          <Link href="/activity-logs" className="text-base font-medium text-gray-500 hover:text-gray-900">
            Activity Logs
          </Link>
        </div>
      </nav>
    </header>
  )
}