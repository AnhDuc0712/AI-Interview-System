import { useMemo, useState } from 'react';

import type { CVStatus } from '../features/cvs/api/types';
import CVList from '../features/cvs/components/CVList';
import CVUploadCard from '../features/cvs/components/CVUploadCard';
import { useMyCVs } from '../features/cvs/hooks/useMyCVs';
import ErrorState from '../shared/components/ErrorState';
import LoadingState from '../shared/components/LoadingState';

const statusOptions: Array<CVStatus | 'all'> = ['all', 'pending', 'processing', 'completed', 'failed'];

const MyCVsPage = () => {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<CVStatus | 'all'>('all');
  const [search, setSearch] = useState('');
  const cvsQuery = useMyCVs({ page, limit: 9, status });

  const filteredCVs = useMemo(() => {
    const items = cvsQuery.data?.items ?? [];
    const query = search.trim().toLowerCase();
    if (!query) {
      return items;
    }

    return items.filter((cv) => {
      const skills = cv.normalized_content?.skills.join(' ').toLowerCase() ?? '';
      return (
        cv.original_file.original_filename.toLowerCase().includes(query) ||
        skills.includes(query) ||
        cv.status.toLowerCase().includes(query)
      );
    });
  }, [cvsQuery.data?.items, search]);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <section className="flex flex-col gap-4 rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">My CVs</p>
          <h1 className="mt-2 text-3xl font-semibold text-slate-950">Your saved resume history</h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-500">
            Browse every uploaded version, track parser status, and reopen structured CV records after reload.
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:w-[28rem]">
          <input
            className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-400 focus:bg-white"
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search filenames or skills"
            value={search}
          />
          <select
            className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-400 focus:bg-white"
            onChange={(event) => {
              setPage(1);
              setStatus(event.target.value as CVStatus | 'all');
            }}
            value={status}
          >
            {statusOptions.map((option) => (
              <option key={option} value={option}>
                {option === 'all' ? 'All statuses' : option}
              </option>
            ))}
          </select>
        </div>
      </section>

      <div className="mt-8 grid gap-8 xl:grid-cols-[0.8fr_1.2fr]">
        <CVUploadCard />
        <section className="space-y-5">
          {cvsQuery.isLoading ? <LoadingState title="Loading CV history" description="Fetching your saved CV records." /> : null}
          {cvsQuery.error ? (
            <ErrorState
              actionLabel="Retry"
              description="We couldn't load your CV history."
              onAction={() => void cvsQuery.refetch()}
            />
          ) : null}
          {!cvsQuery.isLoading && !cvsQuery.error ? <CVList cvs={filteredCVs} /> : null}

          {cvsQuery.data ? (
            <div className="flex items-center justify-between rounded-3xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
              <p className="text-sm text-slate-500">
                Page {cvsQuery.data.pagination.page} of {cvsQuery.data.pagination.total_pages} · {cvsQuery.data.pagination.total} total CVs
              </p>
              <div className="flex gap-2">
                <button
                  className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-blue-200 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50"
                  disabled={page <= 1}
                  onClick={() => setPage((current) => Math.max(1, current - 1))}
                  type="button"
                >
                  Previous
                </button>
                <button
                  className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-blue-200 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50"
                  disabled={page >= cvsQuery.data.pagination.total_pages}
                  onClick={() => setPage((current) => current + 1)}
                  type="button"
                >
                  Next
                </button>
              </div>
            </div>
          ) : null}
        </section>
      </div>
    </main>
  );
};

export default MyCVsPage;
