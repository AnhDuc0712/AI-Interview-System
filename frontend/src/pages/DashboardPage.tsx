import { useNavigate } from 'react-router-dom';

import CVList from '../features/cvs/components/CVList';
import CVSection from '../features/cvs/components/CVSection';
import CVStatusBadge from '../features/cvs/components/CVStatusBadge';
import CVUploadCard from '../features/cvs/components/CVUploadCard';
import { useMyCVs } from '../features/cvs/hooks/useMyCVs';
import ErrorState from '../shared/components/ErrorState';
import LoadingState from '../shared/components/LoadingState';
import { useMyProfile } from '../features/profile/hooks/useMyProfile';

const DashboardPage = () => {
  const navigate = useNavigate();
  const profileQuery = useMyProfile();
  const recentCVsQuery = useMyCVs({ page: 1, limit: 3 });

  if (profileQuery.isLoading || recentCVsQuery.isLoading) {
    return <LoadingState title="Loading workspace" description="Preparing your AI Career Workspace." />;
  }

  if (profileQuery.error || recentCVsQuery.error || !profileQuery.data || !recentCVsQuery.data) {
    return (
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <ErrorState
          actionLabel="Retry"
          description="We couldn't load your workspace. Please try again."
          onAction={() => {
            void profileQuery.refetch();
            void recentCVsQuery.refetch();
          }}
        />
      </main>
    );
  }

  const { user, profile_completion: profileCompletion } = profileQuery.data;
  const recentCVs = recentCVsQuery.data.items;
  const parsedSkills = Array.from(
    new Set(recentCVs.flatMap((cv) => cv.normalized_content?.skills ?? []))
  ).slice(0, 8);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <section className="rounded-[2rem] border border-blue-100 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.16),_transparent_40%),linear-gradient(135deg,_#ffffff,_#eff6ff)] p-8 shadow-sm">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-blue-600">AI Career Workspace</p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-950">
              Your interview-ready profile starts with a clean CV pipeline.
            </h1>
            <p className="mt-4 max-w-2xl text-base text-slate-600">
              Upload a resume, keep your parsed versions organized, and build a stable foundation for the next AI workflow.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-3xl bg-white/90 p-4 shadow-sm">
              <p className="text-sm text-slate-500">Profile completion</p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">{profileCompletion.score}%</p>
            </div>
            <div className="rounded-3xl bg-white/90 p-4 shadow-sm">
              <p className="text-sm text-slate-500">CV history</p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">{recentCVsQuery.data.pagination.total}</p>
            </div>
            <div className="rounded-3xl bg-white/90 p-4 shadow-sm">
              <p className="text-sm text-slate-500">Latest role target</p>
              <p className="mt-2 text-lg font-semibold text-slate-950">{user.profile.target_role || 'Not set yet'}</p>
            </div>
          </div>
        </div>
      </section>

      <div className="mt-8 grid gap-8 xl:grid-cols-[1.25fr_0.75fr]">
        <div className="space-y-8">
          <CVUploadCard onSuccess={(publicId) => navigate(`/cvs/${publicId}`)} />
          <CVSection
            description="Your most recent parsed resumes, always available after reload."
            title="Recent CVs"
          >
            <CVList cvs={recentCVs} />
          </CVSection>
        </div>

        <div className="space-y-8">
          <CVSection title="Processing status" description="Track the latest ingestion lifecycle at a glance.">
            <div className="space-y-4">
              {recentCVs.map((cv) => (
                <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3" key={cv.public_id}>
                  <div>
                    <p className="font-medium text-slate-900">{cv.original_file.original_filename}</p>
                    <p className="text-sm text-slate-500">{cv.parser.parser_version}</p>
                  </div>
                  <CVStatusBadge status={cv.status} />
                </div>
              ))}
            </div>
          </CVSection>

          <CVSection title="Profile completion" description="Keep your candidate profile AI-ready for downstream workflows.">
            <div className="space-y-4">
              <div>
                <div className="mb-2 flex items-center justify-between text-sm text-slate-600">
                  <span>Completion</span>
                  <span>{profileCompletion.fields_completed}/{profileCompletion.fields_total} fields</span>
                </div>
                <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-blue-600"
                    style={{ width: `${profileCompletion.score}%` }}
                  />
                </div>
              </div>
              <div className="rounded-2xl bg-blue-50 p-4 text-sm text-blue-900">
                <p className="font-semibold">{user.clerk.profile.full_name || user.clerk.email}</p>
                <p className="mt-1 text-blue-700">{user.profile.headline || 'Add a profile headline to strengthen your workspace context.'}</p>
              </div>
            </div>
          </CVSection>

          <CVSection title="Parsed skills preview" description="Top skills inferred from your saved CV history.">
            <div className="flex flex-wrap gap-2">
              {parsedSkills.length > 0 ? (
                parsedSkills.map((skill) => (
                  <span
                    className="rounded-full bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700"
                    key={skill}
                  >
                    {skill}
                  </span>
                ))
              ) : (
                <p className="text-sm text-slate-500">Upload a CV to start seeing parsed skills here.</p>
              )}
            </div>
          </CVSection>
        </div>
      </div>
    </main>
  );
};

export default DashboardPage;
