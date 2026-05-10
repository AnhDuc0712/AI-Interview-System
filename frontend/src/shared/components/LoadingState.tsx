type LoadingStateProps = {
  title?: string;
  description?: string;
};

const LoadingState = ({
  title = 'Loading',
  description = 'Fetching the latest workspace data.'
}: LoadingStateProps) => (
  <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
    <div className="flex items-center gap-4">
      <div className="h-10 w-10 animate-spin rounded-full border-2 border-slate-200 border-t-blue-600" />
      <div>
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        <p className="text-sm text-slate-500">{description}</p>
      </div>
    </div>
  </div>
);

export default LoadingState;
