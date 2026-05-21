import { Clock3, Flame, Layers3, Sparkles, Star, Target } from 'lucide-react';

import type { SkillSuggestion } from '../api/types';
import {
  formatLearningTime,
  getCategoryClasses,
  getDifficultyClasses,
  getPriorityStars,
  normalizeMarketDemand,
  startCase
} from '../utils/skillInsights';
import { LearningPlanButton } from './LearningPlanButton';

type SuggestionCardProps = {
  suggestion: SkillSuggestion;
  isInLearningPlan?: boolean;
  onToggleLearningPlan?: (skill: string) => void;
};

export function SuggestionCard({
  suggestion,
  isInLearningPlan = false,
  onToggleLearningPlan
}: SuggestionCardProps) {
  const demandPercent = normalizeMarketDemand(suggestion.market_demand);
  const priorityStars = getPriorityStars(suggestion.priority);

  return (
    <article className="group rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-sm transition duration-200 hover:-translate-y-1 hover:shadow-lg">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-lg font-semibold text-slate-950">{suggestion.skill}</h3>
            <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${getCategoryClasses(suggestion.category)}`}>
              <Layers3 className="mr-1 h-3.5 w-3.5" aria-hidden="true" />
              {startCase(suggestion.category)}
            </span>
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-600">{suggestion.reason}</p>
        </div>
        <div className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
          {priorityStars.map((isActive, index) => (
            <Star
              key={`${suggestion.skill}-priority-${index}`}
              className={`h-3.5 w-3.5 ${isActive ? 'fill-amber-400 text-amber-400' : 'text-slate-300'}`}
              aria-hidden="true"
            />
          ))}
        </div>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="rounded-2xl bg-slate-50 p-3">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            <span className="inline-flex items-center gap-1">
              <Target className="h-3.5 w-3.5" aria-hidden="true" />
              Market Demand
            </span>
            <span>{demandPercent}%</span>
          </div>
          <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-200">
            <div className="h-full rounded-full bg-gradient-to-r from-blue-500 to-emerald-400" style={{ width: `${demandPercent}%` }} />
          </div>
        </div>

        <div className="rounded-2xl bg-slate-50 p-3">
          <div className="flex items-center justify-between gap-3 text-sm">
            <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${getDifficultyClasses(suggestion.difficulty)}`}>
              <Flame className="mr-1 h-3.5 w-3.5" aria-hidden="true" />
              {suggestion.difficulty}
            </span>
            <span className="inline-flex items-center gap-1 text-slate-600">
              <Clock3 className="h-4 w-4" aria-hidden="true" />
              {formatLearningTime(suggestion.estimated_learning_time_hours)}
            </span>
          </div>
        </div>
      </div>

      {suggestion.related_skills.length ? (
        <div className="mt-4">
          <p className="mb-2 inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
            Related Skills
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestion.related_skills.map((skill) => (
              <span
                className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 ring-1 ring-blue-100"
                key={`${suggestion.skill}-${skill}`}
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      <div className="mt-5 flex items-center justify-between gap-4">
        <div className="text-xs text-slate-500">
          Suggested for stronger role alignment and better ATS coverage.
        </div>
        <LearningPlanButton
          isAdded={isInLearningPlan}
          onToggle={() => onToggleLearningPlan?.(suggestion.skill)}
        />
      </div>
    </article>
  );
}

export default SuggestionCard;
