import { useHealthQuery } from '../shared/hooks/useHealth';

const HomePage = () => {
  const { data, isLoading, error } = useHealthQuery();

  return (
    <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <section className="rounded-[2rem] border border-blue-100 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.16),_transparent_40%),linear-gradient(135deg,_#ffffff,_#eff6ff)] p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-blue-600">AI Career Workspace</p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-slate-950">
          From login to parsed CV, without breaking the workflow.
        </h1>
        <p className="mt-4 max-w-2xl text-base text-slate-600">
          Phase 1 gives each user a real AI-ready path: authenticate, upload a CV, track processing, inspect structured parsing, and reopen history anytime.
        </p>
        <div className="mt-8 rounded-3xl bg-white/90 p-5 text-sm text-slate-700 shadow-sm">
          {isLoading && 'Checking backend status...'}
          {error && 'Unable to reach the backend. Confirm that the API is running.'}
          {data && (
            <div>
              <p className="font-medium text-slate-900">Backend Health</p>
              <p>Status: {data.status}</p>
              <p>Database connected: {String(data.database)}</p>
            </div>
          )}
        </div>
      </section>
    </main>
  );
};

export default HomePage;
