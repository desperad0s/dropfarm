import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { logout } from "@/lib/api"

export function Header() {
  const router = useRouter()

  const handleLogout = async () => {
    try {
      await logout()
      router.push("/login")
    } catch (error) {
      console.error("Failed to logout", error)
    }
  }

  return (
    <header className="bg-card text-card-foreground shadow-md py-4 px-6 flex justify-between items-center">
      <h1 className="text-2xl font-bold">Dropfarm</h1>
      <Button onClick={handleLogout}>Logout</Button>
    </header>
  )
}