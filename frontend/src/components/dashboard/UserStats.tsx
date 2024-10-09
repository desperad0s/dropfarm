import React from 'react';

interface UserStatsProps {
  totalRoutineRuns: number;
  lastRunDate: string;
}

export const UserStats: React.FC<UserStatsProps> = ({ totalRoutineRuns, lastRunDate }) => {
  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h2 className="text-xl font-semibold mb-4">User Stats</h2>
      <p className="text-sm text-gray-600">Total Routine Runs: {totalRoutineRuns}</p>
      <p className="text-sm text-gray-600">Last Run Date: {lastRunDate}</p>
    </div>
  );
};