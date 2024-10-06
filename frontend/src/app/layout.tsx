import '@/styles/globals.css'
import { Inter } from 'next/font/google'
import { Sidebar } from "@/components/sidebar"
import { AuthButton } from "@/components/auth-button"

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex h-screen bg-background">
          <Sidebar />
          <main className="flex-1 overflow-y-auto">
            <div className="flex justify-end p-4">
              <AuthButton />
            </div>
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}