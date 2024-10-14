import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type UserStatsProps = {
  totalRoutineRuns: number
  lastRunDate: string | null
  totalTokensGenerated: number
}

export function UserStats({ totalRoutineRuns, lastRunDate, totalTokensGenerated }: UserStatsProps) {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">User Stats</h2>
      <p>Total Routine Runs: {totalRoutineRuns}</p>
      <p>Last Run Date: {lastRunDate ? new Date(lastRunDate).toLocaleString() : 'N/A'}</p>
      <p>Total Tokens Generated: {totalTokensGenerated}</p>
    </div>
  )
}
