import { Outlet } from 'react-router-dom';

import { useAppAuth } from './AuthProvider';
import LoadingState from '../../shared/components/LoadingState';

const AuthenticatedLayout = () => {
  const auth = useAppAuth();

  if (!auth.isReady) {
    return (
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <LoadingState
          title="Loading your session"
          description="Waiting for Clerk to finish restoring your authenticated workspace."
        />
      </main>
    );
  }

  return <Outlet />;
};

export default AuthenticatedLayout;
