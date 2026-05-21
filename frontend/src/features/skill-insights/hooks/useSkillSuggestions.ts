import { useQuery } from '@tanstack/react-query';

import { useAppAuth } from '../../auth/AuthProvider';
import { getSkillSuggestions } from '../api/skillInsightsApi';
import type { SkillSuggestionsResponse } from '../api/types';

type UseSkillSuggestionsOptions = {
  careerGoal: string;
  limit?: number;
  enabled?: boolean;
};

export const useSkillSuggestions = ({
  careerGoal,
  limit = 10,
  enabled = true
}: UseSkillSuggestionsOptions) => {
  const auth = useAppAuth();
  const trimmedGoal = careerGoal.trim();

  return useQuery<SkillSuggestionsResponse>({
    queryKey: ['skill-suggestions', auth.userId, trimmedGoal, limit],
    enabled: auth.isReady && enabled && trimmedGoal.length > 0,
    queryFn: () => getSkillSuggestions(auth.getToken, trimmedGoal, limit),
    staleTime: 1000 * 60 * 5
  });
};
