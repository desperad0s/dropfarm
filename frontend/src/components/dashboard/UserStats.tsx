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
      <CardContent className="space-y-2">
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Total Routine Runs</p>
          <p className="text-2xl font-bold">{totalRoutineRuns}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Last Run Date</p>
          <p className="text-lg">{new Date(lastRunDate).toLocaleDateString()}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Total Tokens Generated</p>
          <p className="text-2xl font-bold">{totalTokensGenerated}</p>
        </div>
      </CardContent>
    </Card>
  )
}
