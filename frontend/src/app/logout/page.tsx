"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function LogoutPage() {
  const router = useRouter()

  useEffect(() => {
    // Clear any authentication tokens or user data here
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center py-12 sm:px-6 lg:px-8 bg-background">
      <Card className="w-[350px]">
        <CardHeader>
          <CardTitle>You have been logged out</CardTitle>
          <CardDescription>Thank you for using Dropfarm</CardDescription>
        </CardHeader>
        <CardContent>
          <Button className="w-full" onClick={() => router.push('/login')}>
            Log in again
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}