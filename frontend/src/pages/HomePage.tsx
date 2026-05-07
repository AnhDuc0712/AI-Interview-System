import { useHealthQuery } from '../shared/hooks/useHealth';

const HomePage = () => {
  const { data, isLoading, error } = useHealthQuery();

  return (
    <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-3xl font-semibold text-slate-900">AI Interview System</h1>
        <p className="mt-4 text-slate-600">
          Welcome to the foundation build for the AI Interview System.
        </p>
        <div className="mt-8 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
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
