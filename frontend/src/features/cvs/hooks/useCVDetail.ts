import { useQuery } from '@tanstack/react-query';

import { useAppAuth } from '../../auth/AuthProvider';
import { getCVDetail } from '../api/cvApi';

export const useCVDetail = (publicId: string) => {
  const auth = useAppAuth();

  return useQuery({
    queryKey: ['cvs', 'detail', auth.userId, publicId],
    enabled: auth.isReady && Boolean(publicId),
    queryFn: () => getCVDetail(auth.getToken, publicId)
  });
};
