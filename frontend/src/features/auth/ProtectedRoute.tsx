import type { ReactNode } from 'react';

import { RedirectToSignIn } from '@clerk/clerk-react';
import { Outlet } from 'react-router-dom';

import LoadingState from '../../shared/components/LoadingState';
import { useAppAuth } from './AuthProvider';

type ProtectedRouteProps = {
  children?: ReactNode;
};

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const auth = useAppAuth();

  if (!auth.isLoaded) {
    return (
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <LoadingState
          title="Restoring authentication"
          description="Clerk is preparing your session before any protected API calls run."
        />
      </main>
    );
  }

  if (!auth.isSignedIn) {
    return <RedirectToSignIn />;
  }

  return children ? <>{children}</> : <Outlet />;
};
