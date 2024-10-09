import LoginForm from '@/components/loginform';
import Link from 'next/link';

export default function LoginPage() {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-6">
        <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">Welcome Back</h1>
        <LoginForm />
        <p className="mt-6 text-center text-gray-600">
          Don't have an account?{' '}
          <Link href="/register" className="text-blue-500 hover:underline font-medium">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}