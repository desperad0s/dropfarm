import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { ModeToggle } from "@/components/mode-toggle"
import { Button } from "@/components/ui/button"
import Link from "next/link"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Dropfarm Dashboard",
  description: "Monitor and control your Dropfarm bots",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="min-h-screen flex flex-col">
            <header className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
              <div className="container mx-auto px-4 flex justify-between items-center h-16">
                <Link href="/" className="font-bold text-2xl">
                  Dropfarm
                </Link>
                <nav className="flex space-x-4">
                  <Link href="/" className="text-sm font-medium">Dashboard</Link>
                  <Link href="/projects" className="text-sm font-medium">Projects</Link>
                  <Link href="/settings" className="text-sm font-medium">Settings</Link>
                </nav>
                <div className="flex items-center space-x-4">
                  <ModeToggle />
                  <Button variant="outline" asChild>
                    <Link href="/logout">Logout</Link>
                  </Button>
                </div>
              </div>
            </header>
            <main className="flex-grow pt-16 container mx-auto px-4">
              {children}
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
}