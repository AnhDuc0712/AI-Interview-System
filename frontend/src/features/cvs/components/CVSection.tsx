import { ReactNode } from 'react';

type CVSectionProps = {
  title: string;
  description?: string;
  children: ReactNode;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

export const renderSafeValue = (value: unknown, fallback = 'Not detected'): string => {
  if (value === null || value === undefined) return fallback;
  if (typeof value === 'string') return value.trim() || fallback;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (Array.isArray(value)) {
    const rendered = value
      .map((item) => renderSafeValue(item, ''))
      .filter(Boolean)
      .join(', ');
    return rendered || fallback;
  }
  if (isRecord(value)) {
    const preferred = value.name ?? value.title ?? value.label ?? value.value ?? value.institution ?? value.company;
    if (typeof preferred === 'string' && preferred.trim()) {
      return preferred.trim();
    }
    return fallback;
  }
  return fallback;
};

export const getSafeItemKey = (prefix: string, value: unknown, index: number): string => {
  const normalizedValue = renderSafeValue(value, '');
  return `${prefix}-${normalizedValue || 'item'}-${index}`;
};

const CVSection = ({ title, description, children }: CVSectionProps) => (
  <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
    <div className="mb-5">
      <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
      {description ? <p className="mt-2 text-sm text-slate-500">{description}</p> : null}
    </div>
    {children}
  </section>
);

export default CVSection;
