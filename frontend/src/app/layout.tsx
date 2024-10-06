import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex h-screen bg-background">
          <Sidebar />
          <div className="flex-1 flex flex-col overflow-hidden">
            <Header />
            <main className="flex-1 overflow-x-hidden overflow-y-auto bg-background">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  )
}