'use client'

import { useAuth } from '@/contexts/AuthContext';
import { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { session, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !session && pathname !== '/login') {
      router.push('/login');
    }
  }, [session, loading, router, pathname]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return session ? <>{children}</> : null;
}