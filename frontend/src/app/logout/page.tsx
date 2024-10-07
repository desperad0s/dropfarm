"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from 'next/link'
import LoginForm from "@/components/LoginForm"

export default function LogoutPage() {
  const router = useRouter()

  useEffect(() => {
    // Clear any authentication tokens or user data here
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center py-12 sm:px-6 lg:px-8 bg-background">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-foreground">You have been logged out</h2>
        <p className="mt-2 text-center text-sm text-muted-foreground">
          To use the bot, please log in or sign up.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-card py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <LoginForm />
        </div>
      </div>
    </div>
  )
}