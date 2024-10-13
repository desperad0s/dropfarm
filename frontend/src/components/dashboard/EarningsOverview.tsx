import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type EarningsOverviewProps = {
  totalEarnings: number
  earningsHistory: { date: string; amount: number }[]
  totalTokensGenerated: number
}

export function EarningsOverview({ totalEarnings, earningsHistory, totalTokensGenerated }: EarningsOverviewProps) {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Earnings Overview</h2>
      <p className="text-2xl font-bold">${totalEarnings.toFixed(2)}</p>
      <p className="text-sm text-gray-500 dark:text-gray-400">Total Earnings</p>
      <p className="text-lg mt-2">{totalTokensGenerated}</p>
      <p className="text-sm text-gray-500 dark:text-gray-400">Total Tokens Generated</p>
    </div>
  )
}
