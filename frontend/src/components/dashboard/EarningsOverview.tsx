import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type EarningsOverviewProps = {
  totalEarnings: number
  earningsHistory: { date: string; amount: number }[]
  totalTokensGenerated: number
}

export function EarningsOverview({ totalEarnings, earningsHistory, totalTokensGenerated }: EarningsOverviewProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Earnings Overview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <p className="text-2xl font-bold">${totalEarnings.toFixed(2)}</p>
        <p className="text-sm text-gray-500 dark:text-gray-400">Total Earnings</p>
        <p className="text-lg">{totalTokensGenerated}</p>
        <p className="text-sm text-gray-500 dark:text-gray-400">Total Tokens Generated</p>
      </CardContent>
    </Card>
  )
}
