import { createContext, useContext, type ReactNode } from 'react';

import { useAuth } from '@clerk/clerk-react';

import type { TokenProvider } from '../../shared/api/apiClient';

type AuthContextValue = {
  isLoaded: boolean;
  isSignedIn: boolean;
  isReady: boolean;
  userId: string | null | undefined;
  getToken: TokenProvider;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const { getToken, isLoaded, isSignedIn, userId } = useAuth();

  const authContextValue: AuthContextValue = {
    isLoaded,
    isSignedIn: Boolean(isSignedIn),
    isReady: isLoaded && Boolean(isSignedIn),
    userId,
    getToken: async () => {
      if (!isLoaded || !isSignedIn) {
        return null;
      }

      return getToken({
        skipCache: true
      });
    }
  };

  return <AuthContext.Provider value={authContextValue}>{children}</AuthContext.Provider>;
};

export const useAppAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAppAuth must be used within AuthProvider');
  }

  return context;
};
