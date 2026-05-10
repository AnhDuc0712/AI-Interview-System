type ErrorStateProps = {
  title?: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
};

const ErrorState = ({
  title = 'Something went wrong',
  description,
  actionLabel,
  onAction
}: ErrorStateProps) => (
  <div className="rounded-3xl border border-rose-200 bg-rose-50 p-8 text-rose-900 shadow-sm">
    <h3 className="text-lg font-semibold">{title}</h3>
    <p className="mt-2 text-sm text-rose-700">{description}</p>
    {actionLabel && onAction ? (
      <button
        className="mt-5 rounded-full bg-rose-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-500"
        onClick={onAction}
        type="button"
      >
        {actionLabel}
      </button>
    ) : null}
  </div>
);

export default ErrorState;
