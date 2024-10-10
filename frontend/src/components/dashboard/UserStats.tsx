import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type UserStatsProps = {
  totalRoutineRuns: number
  lastRunDate: string
  totalTokensGenerated: number
}

export function UserStats({ totalRoutineRuns, lastRunDate, totalTokensGenerated }: UserStatsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>User Stats</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Total Routine Runs: {totalRoutineRuns}</p>
        <p>Last Run Date: {lastRunDate}</p>
        <p>Total Tokens Generated: {totalTokensGenerated}</p>
      </CardContent>
    </Card>
  )
}