import { ReactNode } from 'react';
import { RedirectToSignIn, SignedIn, SignedOut } from '@clerk/clerk-react';

export const ProtectedRoute = ({ children }: { children: ReactNode }) => (
  <>
    <SignedIn>{children}</SignedIn>
    <SignedOut>
      <RedirectToSignIn />
    </SignedOut>
  </>
);
