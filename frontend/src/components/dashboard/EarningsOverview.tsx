import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type EarningsOverviewProps = {
  totalTokensGenerated: number
}

export function EarningsOverview({ totalTokensGenerated }: EarningsOverviewProps) {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Tokens Overview</h2>
      <p className="text-2xl font-bold">{totalTokensGenerated}</p>
      <p className="text-sm text-gray-500 dark:text-gray-400">Total Tokens Generated</p>
    </div>
  )
}
