'use client';

import RegisterForm from '@/components/registerform';
import Link from 'next/link';

export default function RegisterPage() {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-6">
        <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">Create an Account</h1>
        <RegisterForm />
        <p className="mt-6 text-center text-gray-600">
          Already have an account?{' '}
          <Link href="/login" className="text-blue-500 hover:underline font-medium">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}