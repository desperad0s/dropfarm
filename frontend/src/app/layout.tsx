import { Inter } from 'next/font/google'
import './globals.css'
import ClientLayout from '@/components/ClientLayout'
import { AuthProvider } from '@/contexts/AuthContext'

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: 'Dropfarm',
  description: 'Automated airdrop farming',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <ClientLayout>{children}</ClientLayout>
        </AuthProvider>
      </body>
    </html>
  )
}