import '@/styles/globals.css'
import { Inter } from 'next/font/google'
import { Sidebar } from "@/components/sidebar"
import { AuthButton } from "@/components/auth-button"
import { ThemeToggle } from "@/components/theme-toggle"
import { ThemeProvider } from "@/components/theme-provider"

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <div className="flex h-screen bg-background text-foreground">
            <Sidebar />
            <main className="flex-1 overflow-y-auto">
              <div className="flex justify-end items-center p-4 space-x-2">
                <ThemeToggle />
                <AuthButton />
              </div>
              {children}
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
}