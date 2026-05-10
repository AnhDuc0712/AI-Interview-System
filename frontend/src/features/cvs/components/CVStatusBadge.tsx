import type { CVStatus } from '../api/types';

const statusStyles: Record<CVStatus, string> = {
  pending: 'bg-amber-100 text-amber-800',
  processing: 'bg-blue-100 text-blue-800',
  completed: 'bg-emerald-100 text-emerald-800',
  failed: 'bg-rose-100 text-rose-800'
};

type CVStatusBadgeProps = {
  status: CVStatus;
};

const CVStatusBadge = ({ status }: CVStatusBadgeProps) => (
  <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold capitalize ${statusStyles[status]}`}>
    {status}
  </span>
);

export default CVStatusBadge;
