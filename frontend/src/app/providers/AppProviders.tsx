import type { ReactNode } from 'react';

import { ClerkProvider } from '@clerk/clerk-react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

import { AuthProvider } from '../../features/auth/AuthProvider';
import { ApiError } from '../../shared/api/apiClient';

const clerkPublishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        if (error instanceof ApiError && error.status === 401) {
          return false;
        }

        return failureCount < 1;
      },
      refetchOnWindowFocus: false
    },
    mutations: {
      retry: (failureCount, error) => {
        if (error instanceof ApiError && error.status === 401) {
          return false;
        }

        return failureCount < 1;
      }
    }
  }
});

export const AppProviders = ({ children }: { children: ReactNode }) => {
  return (
    <ClerkProvider publishableKey={clerkPublishableKey || ''}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <BrowserRouter>{children}</BrowserRouter>
        </AuthProvider>
      </QueryClientProvider>
    </ClerkProvider>
  );
};
