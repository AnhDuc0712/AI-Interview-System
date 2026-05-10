import type { CVRecord } from '../api/types';
import EmptyState from '../../../shared/components/EmptyState';
import CVCard from './CVCard';

type CVListProps = {
  cvs: CVRecord[];
};

const CVList = ({ cvs }: CVListProps) => {
  if (cvs.length === 0) {
    return (
      <EmptyState
        title="No CVs yet"
        description="Upload your first CV to start building a persistent AI-ready career workspace."
      />
    );
  }

  return (
    <div className="grid gap-4">
      {cvs.map((cv) => (
        <CVCard cv={cv} key={cv.public_id} />
      ))}
    </div>
  );
};

export default CVList;
