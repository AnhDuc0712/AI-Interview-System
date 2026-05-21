import type { ReactNode } from 'react';
import { useMemo } from 'react';
import { AlertCircle, BriefcaseBusiness, DatabaseZap, ShieldCheck, Sparkles, Target } from 'lucide-react';

import type { CVRecord } from '../../cvs/api/types';
import ErrorState from '../../../shared/components/ErrorState';
import LoadingState from '../../../shared/components/LoadingState';
import { useAppStore } from '../../../shared/store/useAppStore';
import { useATSScore } from '../hooks/useATSScore';
import { useSkillSuggestions } from '../hooks/useSkillSuggestions';
import { extractTargetSkills } from '../utils/skillInsights';
import SkillRadarChart from './SkillRadarChart';
import SmartCacheIndicator from './SmartCacheIndicator';
import SuggestionCard from './SuggestionCard';

type ATSDashboardProps = {
  selectedCV: CVRecord | null;
  careerGoal: string;
};

function MetricCard({
  title,
  value,
  icon,
  accentClass
}: {
  title: string;
  value: number;
  icon: ReactNode;
  accentClass: string;
}) {
  return (
    <div className="rounded-[1.5rem] border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-slate-950">{value}%</p>
        </div>
        <div className={`rounded-2xl p-3 ${accentClass}`}>{icon}</div>
      </div>
    </div>
  );
}

function SuggestionSkeleton() {
  return (
    <div className="rounded-[1.75rem] border border-slate-200 bg-white p-5 shadow-sm">
      <div className="animate-pulse space-y-4">
        <div className="h-5 w-40 rounded-full bg-slate-200" />
        <div className="h-4 w-full rounded-full bg-slate-100" />
        <div className="h-4 w-3/4 rounded-full bg-slate-100" />
        <div className="h-2 w-full rounded-full bg-slate-100" />
        <div className="flex gap-2">
          <div className="h-8 w-24 rounded-full bg-slate-100" />
          <div className="h-8 w-20 rounded-full bg-slate-100" />
        </div>
      </div>
    </div>
  );
}

export function ATSDashboard({ selectedCV, careerGoal }: ATSDashboardProps) {
  const addSkillToLearningPlan = useAppStore((state) => state.addSkillToLearningPlan);
  const removeSkillFromLearningPlan = useAppStore((state) => state.removeSkillFromLearningPlan);
  const learningPlanSkills = useAppStore((state) => state.learningPlanSkills);

  const cvId = selectedCV?.public_id ?? '';
  const selectedSkills = selectedCV?.normalized_content?.skills ?? [];

  const atsScoreQuery = useATSScore({
    cvId,
    careerGoal,
    enabled: Boolean(selectedCV)
  });
  const suggestionsQuery = useSkillSuggestions({
    careerGoal,
    limit: 10,
    enabled: Boolean(careerGoal.trim())
  });

  const targetSkills = useMemo(
    () => extractTargetSkills(suggestionsQuery.data?.suggestions ?? []),
    [suggestionsQuery.data?.suggestions]
  );

  const toggleLearningPlan = (skill: string) => {
    if (learningPlanSkills.includes(skill)) {
      removeSkillFromLearningPlan(skill);
      return;
    }
    addSkillToLearningPlan(skill);
  };

  if (!selectedCV) {
    return (
      <div className="rounded-[2rem] border border-dashed border-slate-300 bg-white p-10 text-center shadow-sm">
        <BriefcaseBusiness className="mx-auto h-10 w-10 text-slate-400" aria-hidden="true" />
        <h2 className="mt-4 text-xl font-semibold text-slate-950">Select a CV to unlock skill insights</h2>
        <p className="mt-2 text-sm text-slate-500">
          Choose one of your parsed CVs above to compare it with market demand and ATS expectations.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <SmartCacheIndicator />

      <div className="grid gap-8 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-8">
          <SkillRadarChart
            careerGoal={careerGoal}
            targetSkills={targetSkills}
            userSkills={selectedSkills}
          />

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              title="Overall ATS Score"
              value={atsScoreQuery.data?.overall_score ?? 0}
              icon={<Target className="h-6 w-6 text-blue-700" aria-hidden="true" />}
              accentClass="bg-blue-100"
            />
            <MetricCard
              title="Skills Match"
              value={atsScoreQuery.data?.skills_match ?? 0}
              icon={<Sparkles className="h-6 w-6 text-emerald-700" aria-hidden="true" />}
              accentClass="bg-emerald-100"
            />
            <MetricCard
              title="Experience Match"
              value={atsScoreQuery.data?.experience_match ?? 0}
              icon={<ShieldCheck className="h-6 w-6 text-amber-700" aria-hidden="true" />}
              accentClass="bg-amber-100"
            />
            <MetricCard
              title="Market Demand"
              value={atsScoreQuery.data?.market_demand_score ?? 0}
              icon={<DatabaseZap className="h-6 w-6 text-violet-700" aria-hidden="true" />}
              accentClass="bg-violet-100"
            />
          </div>

          {atsScoreQuery.isLoading ? (
            <LoadingState title="Scoring CV against ATS expectations" description="Crunching market demand and skill alignment." />
          ) : null}

          {atsScoreQuery.error ? (
            <ErrorState
              actionLabel="Retry"
              description="We couldn't calculate the ATS score for this CV right now."
              onAction={() => void atsScoreQuery.refetch()}
            />
          ) : null}

          {atsScoreQuery.data ? (
            <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">ATS Summary</p>
                  <h2 className="mt-2 text-2xl font-semibold text-slate-950">Where your CV still has room to grow</h2>
                </div>
                <SmartCacheIndicator variant="badge" />
              </div>

              <div className="mt-5">
                <p className="inline-flex items-center gap-2 text-sm font-semibold text-slate-700">
                  <AlertCircle className="h-4 w-4 text-amber-500" aria-hidden="true" />
                  Skill gaps to prioritize next
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {atsScoreQuery.data.skill_gaps.length ? (
                    atsScoreQuery.data.skill_gaps.map((gap) => (
                      <span
                        className="rounded-full bg-amber-50 px-3 py-1.5 text-sm font-medium text-amber-800 ring-1 ring-amber-100"
                        key={gap}
                      >
                        {gap}
                      </span>
                    ))
                  ) : (
                    <span className="rounded-full bg-emerald-50 px-3 py-1.5 text-sm font-medium text-emerald-700 ring-1 ring-emerald-100">
                      Strong alignment. No major gaps detected.
                    </span>
                  )}
                </div>
              </div>
            </section>
          ) : null}
        </div>

        <section className="rounded-[2rem] border border-slate-200 bg-[linear-gradient(180deg,_#ffffff,_#f8fafc)] p-6 shadow-sm">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">Learning Path</p>
              <h2 className="mt-2 text-2xl font-semibold text-slate-950">Top skill suggestions</h2>
              <p className="mt-2 text-sm text-slate-500">
                Market-aware recommendations tailored to your selected role target.
              </p>
            </div>
            <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
              {learningPlanSkills.length} in plan
            </div>
          </div>

          <div className="mt-6 max-h-[64rem] space-y-4 overflow-y-auto pr-1">
            {suggestionsQuery.isLoading ? (
              Array.from({ length: 5 }, (_, index) => <SuggestionSkeleton key={`suggestion-skeleton-${index}`} />)
            ) : null}

            {suggestionsQuery.error ? (
              <ErrorState
                actionLabel="Retry"
                description="We couldn't load role-based skill suggestions right now."
                onAction={() => void suggestionsQuery.refetch()}
              />
            ) : null}

            {suggestionsQuery.data?.suggestions.map((suggestion) => (
              <SuggestionCard
                isInLearningPlan={learningPlanSkills.includes(suggestion.skill)}
                key={suggestion.skill}
                onToggleLearningPlan={toggleLearningPlan}
                suggestion={suggestion}
              />
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export default ATSDashboard;
