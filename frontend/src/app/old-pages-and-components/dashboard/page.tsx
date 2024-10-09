"use client"

import React, { useState, useEffect } from 'react'
import { EarningsChart } from '@/components/earnings-chart'
import { useAuth } from '@/hooks/useAuth' // Make sure this hook exists

interface EarningsData {
  total: number
  lastMonth: number
  history: Array<{ date: string; amount: number }>
}

export default function DashboardPage() {
  const [earningsData, setEarningsData] = useState<EarningsData | undefined>(undefined)
  const { token } = useAuth() // Make sure this hook is implemented

  useEffect(() => {
    if (token) {
      fetch('/api/earnings', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
        .then(response => response.json())
        .then(data => setEarningsData(data))
        .catch(error => console.error('Error fetching earnings data:', error))
    }
  }, [token])

  return (
    <div>
      <h1>Dashboard</h1>
      <EarningsChart earningsData={earningsData} />
      {/* Other dashboard components */}
    </div>
  )
}