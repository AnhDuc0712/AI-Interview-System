import { Link } from 'react-router-dom';

import type { CVRecord } from '../api/types';
import { formatDateTime, formatFileSize } from '../utils/formatters';
import CVStatusBadge from './CVStatusBadge';

type CVCardProps = {
  cv: CVRecord;
};

const CVCard = ({ cv }: CVCardProps) => (
  <article className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
    <div className="flex items-start justify-between gap-4">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
          {cv.original_file.file_type.toUpperCase()}
        </p>
        <h3 className="mt-2 text-lg font-semibold text-slate-900">{cv.original_file.original_filename}</h3>
        <p className="mt-1 text-sm text-slate-500">
          Uploaded {formatDateTime(cv.metadata.created_at)} · {formatFileSize(cv.original_file.size_bytes)}
        </p>
      </div>
      <CVStatusBadge status={cv.status} />
    </div>
    <div className="mt-4 grid gap-3 text-sm text-slate-600 sm:grid-cols-2">
      <div>
        <p className="font-medium text-slate-900">Parser</p>
        <p>{cv.parser.parser_version}</p>
      </div>
      <div>
        <p className="font-medium text-slate-900">Skills parsed</p>
        <p>{cv.normalized_content?.skills.length ?? 0}</p>
      </div>
    </div>
    <div className="mt-5 flex items-center justify-between">
      <div className="max-w-[70%] text-sm text-slate-500">
        {cv.normalized_content?.personal_info.summary || 'Structured profile is ready to inspect in detail.'}
      </div>
      <Link
        className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:border-blue-200 hover:bg-blue-50"
        to={`/cvs/${cv.public_id}`}
      >
        View details
      </Link>
    </div>
  </article>
);

export default CVCard;
