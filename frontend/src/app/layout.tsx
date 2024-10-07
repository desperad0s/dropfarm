'use client'

import { useState, useEffect } from "react"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { ModeToggle } from "@/components/mode-toggle"
import Link from "next/link"
import { UserAvatar } from "@/components/Avatar"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { logout, api } from "@/lib/api"

const inter = Inter({ subsets: ["latin"] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [username, setUsername] = useState("")
  const router = useRouter()

  useEffect(() => {
    checkLoginStatus()
  }, [])

  const checkLoginStatus = async () => {
    const token = localStorage.getItem('token')
    if (token) {
      try {
        const response = await api.get('/verify_token')
        setIsLoggedIn(true)
        setUsername(response.data.user)
      } catch (error) {
        console.error('Token verification failed:', error)
        handleLogout()
      }
    } else {
      setIsLoggedIn(false)
      router.push('/login')
    }
  }

  const handleLogout = async () => {
    try {
      await logout()
      setIsLoggedIn(false)
      setUsername("")
      router.push('/logout')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <html lang="en">
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="flex flex-col min-h-screen">
            <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
              <div className="container flex h-14 items-center">
                <Link href="/" className="mr-6 flex items-center space-x-2">
                  <span className="text-2xl font-bold">Dropfarm</span>
                </Link>
                <nav className="flex items-center space-x-6 text-sm font-medium flex-1 justify-center">
                  <Link href="/">Dashboard</Link>
                  <Link href="/projects">Projects</Link>
                  <Link href="/settings">Settings</Link>
                </nav>
                <div className="flex items-center space-x-4">
                  {isLoggedIn && <UserAvatar username={username} />}
                  <ModeToggle />
                  {isLoggedIn ? (
                    <Button variant="outline" size="sm" onClick={handleLogout}>Logout</Button>
                  ) : (
                    <Button variant="outline" size="sm" onClick={() => router.push('/login')}>Login</Button>
                  )}
                </div>
              </div>
            </header>
            <main className="flex-1 container py-8">{children}</main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
}