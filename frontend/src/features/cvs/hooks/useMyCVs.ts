import { useQuery } from '@tanstack/react-query';

import { useAppAuth } from '../../auth/AuthProvider';
import { listMyCVs } from '../api/cvApi';
import type { CVStatus } from '../api/types';

type UseMyCVsOptions = {
  page?: number;
  limit?: number;
  status?: CVStatus | 'all';
};

export const useMyCVs = ({ page = 1, limit = 10, status = 'all' }: UseMyCVsOptions = {}) => {
  const auth = useAppAuth();

  return useQuery({
    queryKey: ['cvs', 'me', auth.userId, page, limit, status],
    enabled: auth.isReady,
    queryFn: () => listMyCVs(auth.getToken, { page, limit, status })
  });
};
