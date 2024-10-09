import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { HomeIcon, BarChartIcon, SettingsIcon } from "lucide-react"

const sidebarItems = [
  { icon: HomeIcon, label: "Home", href: "/" },
  { icon: BarChartIcon, label: "Statistics", href: "/statistics" },
  { icon: SettingsIcon, label: "Settings", href: "/settings" },
]

export function Sidebar() {
  return (
    <aside className="hidden md:flex w-64 flex-col border-r">
      <div className="p-6">
        <h2 className="text-2xl font-bold">Dropfarm</h2>
      </div>
      <ScrollArea className="flex-1">
        <nav className="space-y-2 p-4">
          {sidebarItems.map((item) => (
            <Link key={item.href} href={item.href} passHref>
              <Button variant="ghost" className="w-full justify-start">
                <item.icon className="mr-2 h-4 w-4" />
                {item.label}
              </Button>
            </Link>
          ))}
        </nav>
      </ScrollArea>
    </aside>
  )
}