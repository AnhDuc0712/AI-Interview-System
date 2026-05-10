type EmptyStateProps = {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
};

const EmptyState = ({ title, description, actionLabel, onAction }: EmptyStateProps) => (
  <div className="rounded-3xl border border-dashed border-slate-300 bg-white/80 p-8 text-center shadow-sm">
    <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
    <p className="mt-2 text-sm text-slate-500">{description}</p>
    {actionLabel && onAction ? (
      <button
        className="mt-5 rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700"
        onClick={onAction}
        type="button"
      >
        {actionLabel}
      </button>
    ) : null}
  </div>
);

export default EmptyState;
