import { useQuery } from '@tanstack/react-query';

import { useAppAuth } from '../../auth/AuthProvider';
import { fetchAuthenticatedJson } from '../../../shared/api/apiClient';
import type { UserResponse } from '../api/types';

export const useMyProfile = () => {
  const auth = useAppAuth();

  return useQuery<UserResponse>({
    queryKey: ['profile', 'me', auth.userId],
    enabled: auth.isReady,
    queryFn: () => fetchAuthenticatedJson('/users/me/profile', auth.getToken)
  });
};
