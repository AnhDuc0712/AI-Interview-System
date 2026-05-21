import { useQuery } from '@tanstack/react-query';

import { useAppAuth } from '../../auth/AuthProvider';
import { getATSScore } from '../api/skillInsightsApi';
import type { ATSScoreResponse } from '../api/types';

type UseATSScoreOptions = {
  cvId: string;
  careerGoal: string;
  enabled?: boolean;
};

export const useATSScore = ({ cvId, careerGoal, enabled = true }: UseATSScoreOptions) => {
  const auth = useAppAuth();
  const trimmedGoal = careerGoal.trim();

  return useQuery<ATSScoreResponse>({
    queryKey: ['ats-score', auth.userId, cvId, trimmedGoal],
    enabled: auth.isReady && enabled && cvId.length > 0,
    queryFn: () => getATSScore(auth.getToken, cvId, trimmedGoal),
    staleTime: 1000 * 60 * 3
  });
};
