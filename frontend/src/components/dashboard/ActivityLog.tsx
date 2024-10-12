import React from 'react';

type Activity = {
  id: string;
  user_id: string;
  action_type: string;
  details: string;
  created_at: string;
};

type ActivityLogProps = {
  activities: Activity[];
};

export function ActivityLog({ activities }: ActivityLogProps) {
  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Activity Log</h2>
      <ul className="space-y-2">
        {activities.map((activity) => (
          <li key={activity.id} className="border-b pb-2">
            <p className="font-semibold">{activity.action_type}</p>
            <p className="text-sm">{activity.details}</p>
            <p className="text-xs text-gray-500">{new Date(activity.created_at).toLocaleString()}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
