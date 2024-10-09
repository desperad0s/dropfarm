import React from 'react';

interface Activity {
  timestamp: string;
  action: string;
  result: string;
}

interface ActivityLogProps {
  activities: Activity[];
}

export const ActivityLog: React.FC<ActivityLogProps> = ({ activities }) => {
  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h2 className="text-xl font-semibold mb-4">Activity Log</h2>
      <ul className="space-y-2">
        {activities.map((activity, index) => (
          <li key={index} className="text-sm text-gray-600">
            <span className="font-medium">{new Date(activity.timestamp).toLocaleString()}</span>
            : {activity.action} - {activity.result}
          </li>
        ))}
      </ul>
    </div>
  );
};