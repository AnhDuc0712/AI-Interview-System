import { Link, useNavigate, useParams } from 'react-router-dom';

import { CVRecord } from '../features/cvs/api/types';
import CVSection, { getSafeItemKey, renderSafeValue } from '../features/cvs/components/CVSection';
import CVStatusBadge from '../features/cvs/components/CVStatusBadge';
import { useCVDetail } from '../features/cvs/hooks/useCVDetail';
import { formatDateTime, formatFileSize } from '../features/cvs/utils/formatters';
import ErrorState from '../shared/components/ErrorState';
import LoadingState from '../shared/components/LoadingState';

type ParsedCV = NonNullable<CVRecord['normalized_content']>;
type CertificationItem = ParsedCV['certifications'][number];

const formatDateRange = (startDate?: string | null, endDate?: string | null) => {
  const values = [startDate, endDate].filter(Boolean);
  if (!values.length) return 'Date not detected';
  return values.join(' - ');
};

const formatCertification = (certification: CertificationItem) => {
  const name = renderSafeValue(certification?.name, '');
  const issuer = renderSafeValue(certification?.issuer, '');
  const date = renderSafeValue(certification?.date, '');
  return [name, issuer, date].filter(Boolean).join(' - ') || 'Untitled certification';
};

const CVDetailPage = () => {
  const { publicId = '' } = useParams();
  const navigate = useNavigate();
  const cvDetailQuery = useCVDetail(publicId);

  if (cvDetailQuery.isLoading) {
    return <LoadingState title="Loading CV detail" description="Retrieving your structured CV data." />;
  }

  if (cvDetailQuery.error || !cvDetailQuery.data) {
    return (
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <ErrorState
          actionLabel="Back to CVs"
          description="We couldn't load this CV record."
          onAction={() => navigate('/cvs')}
        />
      </main>
    );
  }

  const { cv } = cvDetailQuery.data;
  const parsed = cv.normalized_content;
  const personalInfo = parsed?.personal_info;
  const fullName = personalInfo?.name || personalInfo?.full_name || 'Not detected';

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-4 rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm lg:flex-row lg:items-start lg:justify-between">
        <div>
          <Link className="text-sm font-semibold text-blue-600 hover:text-blue-700" to="/cvs">
            Back to My CVs
          </Link>
          <h1 className="mt-3 text-3xl font-semibold text-slate-950">{cv.original_file.original_filename}</h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-500">
            Parsed with {cv.parser.parser_name} {cv.parser.parser_version}. This record persists across reloads and is ready for future AI workflows.
          </p>
        </div>
        <CVStatusBadge status={cv.status} />
      </div>

      <div className="mt-8 grid gap-8 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="space-y-8">
          <CVSection title="Basic info">
            <dl className="grid gap-4 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-slate-500">Full name</dt>
                <dd className="mt-1 font-medium text-slate-900">{fullName}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Email</dt>
                <dd className="mt-1 font-medium text-slate-900">{renderSafeValue(personalInfo?.email)}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Phone</dt>
                <dd className="mt-1 font-medium text-slate-900">{renderSafeValue(personalInfo?.phone)}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Location</dt>
                <dd className="mt-1 font-medium text-slate-900">{renderSafeValue(personalInfo?.location)}</dd>
              </div>
            </dl>
            {personalInfo?.summary ? <p className="mt-5 text-sm leading-6 text-slate-600">{personalInfo.summary}</p> : null}
          </CVSection>

          <CVSection title="Processing metadata">
            <dl className="grid gap-4 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-slate-500">Uploaded</dt>
                <dd className="mt-1 font-medium text-slate-900">{formatDateTime(cv.metadata.created_at)}</dd>
              </div>
              <div>
                <dt className="text-slate-500">File size</dt>
                <dd className="mt-1 font-medium text-slate-900">{formatFileSize(cv.original_file.size_bytes)}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Started</dt>
                <dd className="mt-1 font-medium text-slate-900">{formatDateTime(cv.metadata.processing_started_at)}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Completed</dt>
                <dd className="mt-1 font-medium text-slate-900">{formatDateTime(cv.metadata.processing_completed_at)}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Failed</dt>
                <dd className="mt-1 font-medium text-slate-900">{formatDateTime(cv.metadata.failed_at)}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Last error</dt>
                <dd className="mt-1 font-medium text-slate-900">{cv.metadata.last_error || 'None'}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Extractor</dt>
                <dd className="mt-1 font-medium text-slate-900">
                  {cv.extraction.extractor_name} {cv.extraction.extractor_version}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Parser version</dt>
                <dd className="mt-1 font-medium text-slate-900">{cv.parser.parser_version}</dd>
              </div>
            </dl>
          </CVSection>
        </div>

        <div className="space-y-8">
          <CVSection title="Skills">
            <div className="flex flex-wrap gap-2">
              {parsed?.skills?.length ? (
                parsed.skills.map((skill, index) => (
                  <span
                    className="rounded-full bg-blue-50 px-3 py-1.5 text-sm font-medium text-blue-700"
                    key={getSafeItemKey('skill', skill, index)}
                  >
                    {renderSafeValue(skill)}
                  </span>
                ))
              ) : (
                <p className="text-sm text-slate-500">No skills were parsed from this CV.</p>
              )}
            </div>
          </CVSection>

          <CVSection title="Education">
            <div className="space-y-4">
              {parsed?.education?.length ? (
                parsed.education.map((item, index) => (
                  <div className="rounded-2xl bg-slate-50 p-4" key={getSafeItemKey('education', item, index)}>
                    <h3 className="font-semibold text-slate-900">{renderSafeValue(item.institution)}</h3>
                    <p className="mt-1 text-sm text-slate-600">
                      {[item.degree, item.field_of_study].filter(Boolean).join(' - ') || 'Details not detected'}
                    </p>
                    <p className="mt-2 text-sm text-slate-500">
                      {[
                        item.gpa ? `GPA: ${item.gpa}` : null,
                        formatDateRange(item.start_date, item.end_date) !== 'Date not detected'
                          ? formatDateRange(item.start_date, item.end_date)
                          : null,
                      ]
                        .filter(Boolean)
                        .join(' - ') || 'Date not detected'}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">No education entries were parsed.</p>
              )}
            </div>
          </CVSection>

          <CVSection title="Projects">
            <div className="space-y-4">
              {parsed?.projects?.length ? (
                parsed.projects.map((item, index) => (
                  <div className="rounded-2xl bg-slate-50 p-4" key={getSafeItemKey('project', item, index)}>
                    <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
                      <h3 className="font-semibold text-slate-900">{renderSafeValue(item.name)}</h3>
                      <p className="text-sm text-slate-500">{formatDateRange(item.start_date, item.end_date)}</p>
                    </div>
                    <p className="mt-2 text-sm leading-6 text-slate-600">{item.description || 'No description detected.'}</p>
                    {item.technologies?.length ? (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {item.technologies.map((tech, techIndex) => (
                          <span
                            className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700 ring-1 ring-slate-200"
                            key={getSafeItemKey(`project-tech-${index}`, tech, techIndex)}
                          >
                            {renderSafeValue(tech)}
                          </span>
                        ))}
                      </div>
                    ) : null}
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">No projects were parsed.</p>
              )}
            </div>
          </CVSection>

          <CVSection title="Experience">
            <div className="space-y-4">
              {parsed?.experience?.length ? (
                parsed.experience.map((item, index) => (
                  <div className="rounded-2xl bg-slate-50 p-4" key={getSafeItemKey('experience', item, index)}>
                    <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <h3 className="font-semibold text-slate-900">{renderSafeValue(item.title)}</h3>
                        <p className="mt-1 text-sm text-slate-500">{renderSafeValue(item.company, 'Company not detected')}</p>
                      </div>
                      <p className="text-sm text-slate-500">{formatDateRange(item.start_date, item.end_date)}</p>
                    </div>
                    {item.location ? <p className="mt-2 text-sm text-slate-500">{item.location}</p> : null}
                    {item.responsibilities?.length ? (
                      <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-600">
                        {item.responsibilities.map((responsibility, responsibilityIndex) => (
                          <li
                            className="flex gap-3"
                            key={getSafeItemKey(`responsibility-${index}`, responsibility, responsibilityIndex)}
                          >
                            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-400" />
                            <span>{renderSafeValue(responsibility)}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="mt-3 text-sm text-slate-600">{item.description || 'No description detected.'}</p>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">No experience entries were parsed.</p>
              )}
            </div>
          </CVSection>

          <CVSection title="Certifications">
            {parsed?.certifications?.length ? (
              <ul className="space-y-2 text-sm text-slate-700">
                {parsed.certifications.map((item, index) => (
                  <li className="rounded-2xl bg-slate-50 px-4 py-3" key={getSafeItemKey('certification', item, index)}>
                    {formatCertification(item)}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">No certifications were parsed.</p>
            )}
          </CVSection>
        </div>
      </div>
    </main>
  );
};

export default CVDetailPage;
