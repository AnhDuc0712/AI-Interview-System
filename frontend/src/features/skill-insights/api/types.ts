import type { CVRecord } from '../../cvs/api/types';

export type SkillCategory =
  | 'frontend'
  | 'backend'
  | 'database'
  | 'devops'
  | 'mobile'
  | 'cloud'
  | 'ai_ml'
  | 'testing'
  | 'tools'
  | 'other';

export type SkillSuggestion = {
  skill: string;
  category: SkillCategory | string;
  market_demand: number;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced' | string;
  estimated_learning_time_hours: number;
  reason: string;
  related_skills: string[];
  priority: number;
};

export type SkillSuggestionsResponse = {
  suggestions: SkillSuggestion[];
};

export type ATSScoreResponse = {
  overall_score: number;
  skills_match: number;
  experience_match: number;
  market_demand_score: number;
  skill_gaps: string[];
};

export type SkillTaxonomyResponse = {
  taxonomy: Record<string, string[]>;
};

export type CacheStatsResponse = {
  total_unique_cvs: number;
  total_parses: number;
  cache_hit_rate: number;
};

export type CVOption = Pick<CVRecord, 'public_id' | 'original_file' | 'normalized_content' | 'status'>;
