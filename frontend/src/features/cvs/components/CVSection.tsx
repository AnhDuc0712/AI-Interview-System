import { ReactNode } from 'react';

type CVSectionProps = {
  title: string;
  description?: string;
  children: ReactNode;
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
