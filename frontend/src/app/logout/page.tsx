import Link from 'next/link';

export default function LogoutPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background">
      <h1 className="text-4xl font-bold mb-6">You have been logged out</h1>
      <p className="text-xl mb-8">To use the bot, please log in or sign up.</p>
      <div className="space-x-4">
        <Link href="/login" className="btn btn-primary">
          Login
        </Link>
        <Link href="/register" className="btn btn-secondary">
          Sign Up
        </Link>
      </div>
    </div>
  );
}