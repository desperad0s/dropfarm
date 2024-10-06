export interface Project {
  id: number;
  name: string;
  earnings: number;
  status: string;
}

export interface DashboardData {
  activeBots: number;
  activeBotsDiff: number;
  totalEarnings: number;
  earningsDiff: number;
  recentActivities: number;
}

export interface ActivityLog {
  id: number;
  timestamp: string;
  action: string;
}