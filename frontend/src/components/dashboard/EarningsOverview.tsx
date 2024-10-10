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
      <CardContent>
        <p>Total Earnings: ${totalEarnings.toFixed(2)}</p>
        <p>Total Tokens Generated: {totalTokensGenerated}</p>
        {/* Add more detailed breakdown or chart here */}
      </CardContent>
    </Card>
  )
}