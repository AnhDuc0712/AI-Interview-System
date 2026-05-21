import { useEffect, useMemo, useState } from 'react';
import { BrainCircuit, FileSearch, Search, UploadCloud } from 'lucide-react';

import CVUploadCard from '../features/cvs/components/CVUploadCard';
import ATSDashboard from '../features/skill-insights/components/ATSDashboard';
import SmartCacheIndicator from '../features/skill-insights/components/SmartCacheIndicator';
import { useCVList } from '../features/skill-insights/hooks/useCVList';
import { careerGoalSuggestions } from '../features/skill-insights/utils/skillInsights';
import ErrorState from '../shared/components/ErrorState';
import LoadingState from '../shared/components/LoadingState';

export function SkillInsightsPage() {
  const cvListQuery = useCVList();
  const [selectedCvId, setSelectedCvId] = useState('');
  const [careerGoal, setCareerGoal] = useState('Frontend Developer');

  useEffect(() => {
    if (!selectedCvId && cvListQuery.data?.items.length) {
      setSelectedCvId(cvListQuery.data.items[0].public_id);
    }
  }, [cvListQuery.data?.items, selectedCvId]);

  const selectedCV = useMemo(
    () => cvListQuery.data?.items.find((cv) => cv.public_id === selectedCvId) ?? null,
    [cvListQuery.data?.items, selectedCvId]
  );

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <section className="rounded-[2rem] border border-blue-100 bg-[radial-gradient(circle_at_top_right,_rgba(34,197,94,0.18),_transparent_32%),radial-gradient(circle_at_top_left,_rgba(59,130,246,0.14),_transparent_36%),linear-gradient(135deg,_#ffffff,_#eff6ff)] p-8 shadow-sm">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-blue-600">Skill Insights</p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-950">
              Turn parsed CV data into a focused learning roadmap.
            </h1>
            <p className="mt-4 text-base leading-7 text-slate-600">
              Compare your CV with role expectations, see market-aligned gaps, and surface the next best skills to learn.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-3xl bg-white/90 p-4 shadow-sm">
              <p className="text-sm text-slate-500">Tracked CVs</p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">{cvListQuery.data?.pagination.total ?? 0}</p>
            </div>
            <div className="rounded-3xl bg-white/90 p-4 shadow-sm">
              <p className="text-sm text-slate-500">Selected goal</p>
              <p className="mt-2 text-lg font-semibold text-slate-950">{careerGoal}</p>
            </div>
            <div className="rounded-3xl bg-white/90 p-4 shadow-sm">
              <p className="text-sm text-slate-500">Parsed skill count</p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">{selectedCV?.normalized_content?.skills.length ?? 0}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-8 grid gap-8 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-start gap-3">
            <div className="rounded-2xl bg-blue-100 p-3 text-blue-700">
              <FileSearch className="h-5 w-5" aria-hidden="true" />
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-slate-950">Choose your CV and career target</h2>
              <p className="mt-2 text-sm text-slate-500">
                The dashboard updates automatically when you switch documents or role targets.
              </p>
            </div>
          </div>

          {cvListQuery.isLoading ? (
            <div className="mt-6">
              <LoadingState title="Loading CV options" description="Pulling your parsed CV library into the dashboard." />
            </div>
          ) : null}

          {cvListQuery.error ? (
            <div className="mt-6">
              <ErrorState
                actionLabel="Retry"
                description="We couldn't load your CV list for insights."
                onAction={() => void cvListQuery.refetch()}
              />
            </div>
          ) : null}

          {!cvListQuery.isLoading && !cvListQuery.error ? (
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="mb-2 inline-flex items-center gap-2 text-sm font-medium text-slate-700">
                  <BrainCircuit className="h-4 w-4" aria-hidden="true" />
                  Select CV
                </span>
                <select
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-400 focus:bg-white"
                  onChange={(event) => setSelectedCvId(event.target.value)}
                  value={selectedCvId}
                >
                  {cvListQuery.data?.items.map((cv) => (
                    <option key={cv.public_id} value={cv.public_id}>
                      {cv.original_file.original_filename} • {cv.status}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block">
                <span className="mb-2 inline-flex items-center gap-2 text-sm font-medium text-slate-700">
                  <Search className="h-4 w-4" aria-hidden="true" />
                  Career goal
                </span>
                <input
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-400 focus:bg-white"
                  list="career-goal-suggestions"
                  onChange={(event) => setCareerGoal(event.target.value)}
                  placeholder="e.g. Frontend Developer"
                  value={careerGoal}
                />
                <datalist id="career-goal-suggestions">
                  {careerGoalSuggestions.map((goal) => (
                    <option key={goal} value={goal} />
                  ))}
                </datalist>
              </label>
            </div>
          ) : null}
        </div>

        <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-start gap-3">
            <div className="rounded-2xl bg-emerald-100 p-3 text-emerald-700">
              <UploadCloud className="h-5 w-5" aria-hidden="true" />
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-slate-950">Upload a new CV</h2>
              <p className="mt-2 text-sm text-slate-500">
                Smart cache feedback appears automatically after upload, and your CV list refreshes in the selector.
              </p>
              <div className="mt-3">
                <SmartCacheIndicator variant="badge" />
              </div>
            </div>
          </div>

          <div className="mt-6">
            <CVUploadCard
              onSuccess={(publicId) => {
                setSelectedCvId(publicId);
                void cvListQuery.refetch();
              }}
            />
          </div>
        </div>
      </section>

      <section className="mt-8">
        <ATSDashboard careerGoal={careerGoal} selectedCV={selectedCV} />
      </section>
    </main>
  );
}

export default SkillInsightsPage;
