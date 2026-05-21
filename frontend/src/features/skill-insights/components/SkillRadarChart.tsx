import { useMemo } from 'react';
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';

import { useSkillSuggestions } from '../hooks/useSkillSuggestions';
import { useSkillTaxonomy } from '../hooks/useSkillTaxonomy';
import { buildRadarData } from '../utils/skillInsights';

type SkillRadarChartProps = {
  userSkills: string[];
  targetSkills?: string[];
  skillScores?: Record<string, number>;
  careerGoal?: string;
};

type TooltipPayload = Array<{
  payload: {
    category: string;
    yourSkillNames: string[];
    targetSkillNames: string[];
  };
}>;

function RadarTooltip({
  active,
  payload
}: {
  active?: boolean;
  payload?: TooltipPayload;
}) {
  if (!active || !payload?.length) {
    return null;
  }

  const dataPoint = payload[0]?.payload;
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-xl">
      <p className="font-semibold text-slate-900">{dataPoint.category}</p>
      <p className="mt-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Your Skills</p>
      <p className="mt-1 text-sm text-slate-700">{dataPoint.yourSkillNames.join(', ') || 'None mapped yet'}</p>
      <p className="mt-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Target Skills</p>
      <p className="mt-1 text-sm text-slate-700">{dataPoint.targetSkillNames.join(', ') || 'No target skills'}</p>
    </div>
  );
}

export function SkillRadarChart({
  userSkills,
  targetSkills,
  skillScores = {},
  careerGoal
}: SkillRadarChartProps) {
  const taxonomyQuery = useSkillTaxonomy();
  const suggestionsQuery = useSkillSuggestions({
    careerGoal: careerGoal ?? '',
    limit: 12,
    enabled: targetSkills === undefined && Boolean(careerGoal)
  });

  const effectiveTargetSkills = targetSkills ?? (
    suggestionsQuery.data?.suggestions ?? []
  ).map((suggestion) => suggestion.skill);

  const chartData = useMemo(
    () => buildRadarData(userSkills, effectiveTargetSkills, taxonomyQuery.data?.taxonomy, skillScores),
    [effectiveTargetSkills, skillScores, taxonomyQuery.data?.taxonomy, userSkills]
  );

  return (
    <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">Skill Radar</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">Current strengths vs. target role demand</h2>
          <p className="mt-2 text-sm text-slate-500">
            Compare your current skill coverage with market-aligned target skills by category.
          </p>
        </div>
        {careerGoal ? (
          <div className="rounded-full bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700 ring-1 ring-blue-100">
            Career goal: {careerGoal}
          </div>
        ) : null}
      </div>

      <div className="h-[22rem] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={chartData} outerRadius="74%">
            <PolarGrid stroke="#cbd5e1" />
            <PolarAngleAxis dataKey="category" tick={{ fill: '#334155', fontSize: 12 }} />
            <PolarRadiusAxis allowDecimals={false} tick={{ fill: '#64748b', fontSize: 11 }} />
            <Tooltip content={<RadarTooltip />} />
            <Legend />
            <Radar
              name="Your Skills"
              dataKey="yourSkills"
              stroke="#2563eb"
              fill="#3b82f6"
              fillOpacity={0.28}
            />
            <Radar
              name="Market Demand / Target Role"
              dataKey="targetSkills"
              stroke="#10b981"
              fill="#34d399"
              fillOpacity={0.24}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export default SkillRadarChart;
