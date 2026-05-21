import { useQuery } from '@tanstack/react-query';

import { useAppAuth } from '../../auth/AuthProvider';
import { getCVList } from '../api/skillInsightsApi';
import type { CVListResponse } from '../../cvs/api/types';

export const useCVList = () => {
  const auth = useAppAuth();

  return useQuery<CVListResponse>({
    queryKey: ['skill-insights', 'cvs', auth.userId],
    enabled: auth.isReady,
    queryFn: () => getCVList(auth.getToken),
    staleTime: 1000 * 60 * 2
  });
};
