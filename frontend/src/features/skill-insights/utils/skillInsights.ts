import type { SkillCategory, SkillSuggestion } from '../api/types';

export const fallbackSkillTaxonomy: Record<SkillCategory, string[]> = {
  frontend: ['React', 'Next.js', 'TypeScript', 'JavaScript', 'HTML', 'CSS', 'Tailwind CSS', 'Vue.js', 'Angular'],
  backend: ['Node.js', 'Express.js', 'Python', 'FastAPI', 'Java', 'Spring Boot', '.NET', 'ASP.NET Core', 'GraphQL'],
  database: ['MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'SQL Server', 'SQLite'],
  devops: ['Docker', 'Kubernetes', 'CI/CD', 'GitHub Actions', 'Terraform'],
  mobile: ['React Native', 'Flutter', 'SwiftUI', 'Kotlin'],
  cloud: ['AWS', 'Azure', 'Google Cloud', 'Firebase'],
  ai_ml: ['TensorFlow', 'PyTorch', 'scikit-learn', 'OpenCV'],
  testing: ['Jest', 'Cypress', 'Playwright', 'pytest', 'Selenium'],
  tools: ['Git', 'GitHub', 'Postman', 'Jira'],
  other: []
};

export type RadarDatum = {
  category: string;
  yourSkills: number;
  targetSkills: number;
  yourSkillNames: string[];
  targetSkillNames: string[];
};

const normalizeSkill = (skill: string): string => skill.trim().toLowerCase();

export const categoryLabelMap: Record<SkillCategory, string> = {
  frontend: 'Frontend',
  backend: 'Backend',
  database: 'Database',
  devops: 'DevOps',
  mobile: 'Mobile',
  cloud: 'Cloud',
  ai_ml: 'AI / ML',
  testing: 'Testing',
  tools: 'Tools',
  other: 'Other'
};

export const categoryColorMap: Record<SkillCategory, string> = {
  frontend: 'bg-sky-100 text-sky-800 ring-sky-200',
  backend: 'bg-blue-100 text-blue-800 ring-blue-200',
  database: 'bg-emerald-100 text-emerald-800 ring-emerald-200',
  devops: 'bg-violet-100 text-violet-800 ring-violet-200',
  mobile: 'bg-pink-100 text-pink-800 ring-pink-200',
  cloud: 'bg-cyan-100 text-cyan-800 ring-cyan-200',
  ai_ml: 'bg-amber-100 text-amber-800 ring-amber-200',
  testing: 'bg-rose-100 text-rose-800 ring-rose-200',
  tools: 'bg-slate-100 text-slate-800 ring-slate-200',
  other: 'bg-slate-100 text-slate-700 ring-slate-200'
};

export const difficultyColorMap: Record<string, string> = {
  beginner: 'bg-emerald-100 text-emerald-800 ring-emerald-200',
  intermediate: 'bg-amber-100 text-amber-800 ring-amber-200',
  advanced: 'bg-rose-100 text-rose-800 ring-rose-200'
};

export const categorizeSkills = (
  skills: string[],
  taxonomy: Record<string, string[]> = fallbackSkillTaxonomy
): Record<string, string[]> => {
  const categories: Record<string, string[]> = {};
  const normalizedTaxonomy = Object.entries(taxonomy).map(([category, entries]) => ({
    category,
    entries: new Set(entries.map(normalizeSkill))
  }));

  skills.forEach((skill) => {
    const normalized = normalizeSkill(skill);
    const matchedCategory = normalizedTaxonomy.find((entry) => entry.entries.has(normalized))?.category ?? 'other';
    categories[matchedCategory] = [...(categories[matchedCategory] ?? []), skill];
  });

  return categories;
};

export const buildRadarData = (
  userSkills: string[],
  targetSkills: string[],
  taxonomy: Record<string, string[]> = fallbackSkillTaxonomy,
  skillScores: Record<string, number> = {}
): RadarDatum[] => {
  const userByCategory = categorizeSkills(userSkills, taxonomy);
  const targetByCategory = categorizeSkills(targetSkills, taxonomy);
  const allCategories = Array.from(
    new Set([...Object.keys(taxonomy), ...Object.keys(userByCategory), ...Object.keys(targetByCategory)])
  );

  return allCategories.map((category) => {
    const yourSkillNames = userByCategory[category] ?? [];
    const targetSkillNames = targetByCategory[category] ?? [];
    const weightedUserScore = yourSkillNames.reduce((sum, skill) => sum + (skillScores[skill] ?? 1), 0);

    return {
      category: categoryLabelMap[category as SkillCategory] ?? startCase(category),
      yourSkills: weightedUserScore || yourSkillNames.length,
      targetSkills: targetSkillNames.length,
      yourSkillNames,
      targetSkillNames
    };
  });
};

export const formatPercentage = (value: number): string => `${Math.round(value * 100)}%`;

export const formatLearningTime = (hours: number): string => {
  if (hours <= 0) {
    return 'Flexible timeline';
  }
  if (hours < 8) {
    return `${hours} hours`;
  }

  const weeks = Math.ceil(hours / 10);
  return `${hours} hours • about ${weeks} week${weeks > 1 ? 's' : ''}`;
};

export const normalizeMarketDemand = (value: number): number => {
  if (value > 1) {
    return Math.max(0, Math.min(100, value));
  }
  return Math.round(value * 100);
};

export const startCase = (value: string): string =>
  value
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, (character) => character.toUpperCase());

export const getDifficultyClasses = (difficulty: string): string =>
  difficultyColorMap[difficulty.toLowerCase()] ?? 'bg-slate-100 text-slate-700 ring-slate-200';

export const getCategoryClasses = (category: string): string =>
  categoryColorMap[category as SkillCategory] ?? 'bg-slate-100 text-slate-700 ring-slate-200';

export const getPriorityStars = (priority: number): Array<boolean> =>
  Array.from({ length: 5 }, (_, index) => index < Math.max(0, Math.min(5, priority)));

export const extractTargetSkills = (suggestions: SkillSuggestion[]): string[] =>
  suggestions.map((suggestion) => suggestion.skill);

export const careerGoalSuggestions = [
  'Frontend Developer',
  'Backend Developer',
  'Full Stack Developer',
  'DevOps Engineer',
  'Data Engineer',
  'AI Engineer',
  'Mobile Developer',
  'QA Engineer'
] as const;
