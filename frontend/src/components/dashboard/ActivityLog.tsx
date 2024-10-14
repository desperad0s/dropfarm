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
  const getActivityDescription = (activity: Activity) => {
    const details = JSON.parse(activity.details);
    switch (activity.action_type) {
      case 'recording_started':
        return `Started recording routine: ${details.routine_name}`;
      case 'recording_completed':
        return `Completed recording routine: ${details.routine_name}`;
      case 'playback_started':
        return `Started playback of routine: ${details.routine_name}`;
      case 'playback_completed':
        return `Completed playback of routine: ${details.routine_name} (${details.runs_completed} runs, ${details.tokens_generated} tokens)`;
      case 'playback_error':
        return `Error during playback of routine: ${details.routine_name} - ${details.error}`;
      default:
        return `${activity.action_type}: ${JSON.stringify(details)}`;
    }
  };

  return (
    <div className="space-y-2">
      {activities.map((activity) => (
        <div key={activity.id} className="bg-gray-100 p-2 rounded">
          <p>{getActivityDescription(activity)}</p>
          <p className="text-sm text-gray-500">{new Date(activity.created_at).toLocaleString()}</p>
        </div>
      ))}
    </div>
  );
}
