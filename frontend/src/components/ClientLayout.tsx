'use client'

import { ThemeToggle } from "@/components/theme-toggle"

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <nav>
        {/* Your existing nav items */}
        <ThemeToggle />
      </nav>
      {children}
    </div>
  )
}