import { ReactNode } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ClerkProvider } from '@clerk/clerk-react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const clerkPublishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

const queryClient = new QueryClient();

export const AppProviders = ({ children }: { children: ReactNode }) => {
  return (
    <BrowserRouter>
      <ClerkProvider publishableKey={clerkPublishableKey || ''}>
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      </ClerkProvider>
    </BrowserRouter>
  );
};
