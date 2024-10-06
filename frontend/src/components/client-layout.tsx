'use client';

import React from 'react'
import { Header } from './header'

export function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background font-sans antialiased">
      <Header />
      <main className="container mx-auto py-6">{children}</main>
    </div>
  )
}