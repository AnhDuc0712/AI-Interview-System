import { BookPlus, Check } from 'lucide-react';

type LearningPlanButtonProps = {
  isAdded: boolean;
  onToggle: () => void;
};

export function LearningPlanButton({ isAdded, onToggle }: LearningPlanButtonProps) {
  return (
    <button
      aria-pressed={isAdded}
      className={`inline-flex items-center justify-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition ${
        isAdded
          ? 'bg-emerald-100 text-emerald-800 ring-1 ring-emerald-200'
          : 'bg-slate-950 text-white hover:bg-blue-700'
      }`}
      onClick={onToggle}
      type="button"
    >
      {isAdded ? <Check className="h-4 w-4" aria-hidden="true" /> : <BookPlus className="h-4 w-4" aria-hidden="true" />}
      {isAdded ? 'Added to Learning Plan' : 'Add to Learning Plan'}
    </button>
  );
}
