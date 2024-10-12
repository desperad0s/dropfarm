import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

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
    <Card>
      <CardHeader>
        <CardTitle>Activity Log</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[300px]">
          <ul className="space-y-4">
            {activities.map((activity) => (
              <li key={activity.id} className="border-b pb-2">
                <p className="font-semibold">{activity.action_type}</p>
                <p className="text-sm">{activity.details}</p>
                <p className="text-xs text-gray-500">{new Date(activity.created_at).toLocaleString()}</p>
              </li>
            ))}
          </ul>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
