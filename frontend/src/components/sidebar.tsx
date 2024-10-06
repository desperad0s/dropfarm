import Link from "next/link"
import { Home, BarChart2, Settings, Activity, Bell } from "lucide-react"

export function Sidebar() {
  return (
    <div className="bg-card text-card-foreground w-64 space-y-6 py-7 px-2 absolute inset-y-0 left-0 transform -translate-x-full md:relative md:translate-x-0 transition duration-200 ease-in-out">
      <nav>
        <Link href="/" className="flex items-center space-x-2 px-4 py-2 hover:bg-accent">
          <Home className="h-5 w-5" />
          <span>Dashboard</span>
        </Link>
        <Link href="/projects" className="flex items-center space-x-2 px-4 py-2 hover:bg-accent">
          <BarChart2 className="h-5 w-5" />
          <span>Projects</span>
        </Link>
        <Link href="/activity-logs" className="flex items-center space-x-2 px-4 py-2 hover:bg-accent">
          <Activity className="h-5 w-5" />
          <span>Activity Logs</span>
        </Link>
        <Link href="/notifications" className="flex items-center space-x-2 px-4 py-2 hover:bg-accent">
          <Bell className="h-5 w-5" />
          <span>Notifications</span>
        </Link>
        <Link href="/profile" className="flex items-center space-x-2 px-4 py-2 hover:bg-accent">
          <Settings className="h-5 w-5" />
          <span>Profile</span>
        </Link>
      </nav>
    </div>
  )
}