import { Link } from 'react-router-dom';

const NotFoundPage = () => (
  <main className="mx-auto flex min-h-screen max-w-5xl items-center justify-center px-4 py-10 sm:px-6">
    <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm text-center">
      <h1 className="text-3xl font-semibold text-slate-900">Page not found</h1>
      <p className="mt-4 text-slate-600">The page you are looking for could not be found.</p>
      <Link to="/" className="mt-6 inline-flex rounded-lg bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-700">
        Return home
      </Link>
    </div>
  </main>
);

export default NotFoundPage;
