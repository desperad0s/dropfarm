import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

type EarningData = {
  date: string
  amount: number
}

type EarningsOverviewProps = {
  totalEarnings: number
  earningsHistory: EarningData[]
}

export function EarningsOverview({ totalEarnings, earningsHistory }: EarningsOverviewProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Earnings Overview</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <span className="text-2xl font-bold">${totalEarnings.toFixed(2)}</span>
          <span className="text-sm text-muted-foreground ml-2">Total Earnings</span>
        </div>
        <div className="h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={earningsHistory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="amount" stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}