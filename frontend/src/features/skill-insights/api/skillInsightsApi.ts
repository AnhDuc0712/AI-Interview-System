import { fetchAuthenticatedJson, type TokenProvider } from '../../../shared/api/apiClient';
import { listMyCVs } from '../../cvs/api/cvApi';
import type { CVListResponse } from '../../cvs/api/types';
import type {
  ATSScoreResponse,
  CacheStatsResponse,
  SkillSuggestionsResponse,
  SkillTaxonomyResponse
} from './types';
import { fallbackSkillTaxonomy } from '../utils/skillInsights';

export const getSkillSuggestions = async (
  getToken: TokenProvider,
  careerGoal: string,
  limit = 10
): Promise<SkillSuggestionsResponse> => {
  const searchParams = new URLSearchParams({
    career_goal: careerGoal,
    limit: String(limit)
  });

  return fetchAuthenticatedJson(`/skills/suggestions?${searchParams.toString()}`, getToken);
};

export const getATSScore = async (
  getToken: TokenProvider,
  cvId: string,
  careerGoal: string
): Promise<ATSScoreResponse> => {
  const searchParams = new URLSearchParams();
  if (careerGoal.trim()) {
    searchParams.set('career_goal', careerGoal);
  }

  return fetchAuthenticatedJson(`/ats/score/${cvId}?${searchParams.toString()}`, getToken);
};

export const getSkillTaxonomy = async (getToken: TokenProvider): Promise<SkillTaxonomyResponse> => {
  try {
    return await fetchAuthenticatedJson('/skills/taxonomy', getToken);
  } catch {
    return { taxonomy: fallbackSkillTaxonomy };
  }
};

export const getCacheStats = async (getToken: TokenProvider): Promise<CacheStatsResponse> => {
  return fetchAuthenticatedJson('/cache/stats', getToken);
};

export const getCVList = async (getToken: TokenProvider): Promise<CVListResponse> => {
  return listMyCVs(getToken, { page: 1, limit: 100, status: 'all' });
};
