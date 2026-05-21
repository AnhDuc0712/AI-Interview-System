import { useQuery } from '@tanstack/react-query';

import { useAppAuth } from '../../auth/AuthProvider';
import { getSkillTaxonomy } from '../api/skillInsightsApi';
import type { SkillTaxonomyResponse } from '../api/types';
import { fallbackSkillTaxonomy } from '../utils/skillInsights';

export const useSkillTaxonomy = () => {
  const auth = useAppAuth();

  return useQuery<SkillTaxonomyResponse>({
    queryKey: ['skill-taxonomy', auth.userId],
    enabled: auth.isReady,
    queryFn: () => getSkillTaxonomy(auth.getToken),
    staleTime: 1000 * 60 * 30,
    placeholderData: {
      taxonomy: fallbackSkillTaxonomy
    }
  });
};
