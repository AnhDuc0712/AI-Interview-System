import { useEffect, useState } from 'react';
import { CheckCircle2, Clock3, Cpu, Zap } from 'lucide-react';

import { useAppStore } from '../../../shared/store/useAppStore';

type SmartCacheIndicatorProps = {
  variant?: 'toast' | 'badge';
  autoHideMs?: number;
};

const formatProcessingTime = (value: number | null) => {
  if (value === null || Number.isNaN(value)) {
    return 'Fast';
  }
  return `${value.toFixed(2)}s`;
};

export function SmartCacheIndicator({
  variant = 'toast',
  autoHideMs = 5000
}: SmartCacheIndicatorProps) {
  const feedback = useAppStore((state) => state.lastUploadFeedback);
  const clearFeedback = useAppStore((state) => state.clearLastUploadFeedback);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!feedback) {
      setVisible(false);
      return;
    }

    setVisible(true);
    if (variant === 'badge') {
      return;
    }

    const timeout = window.setTimeout(() => {
      setVisible(false);
      clearFeedback();
    }, autoHideMs);

    return () => window.clearTimeout(timeout);
  }, [autoHideMs, clearFeedback, feedback, variant]);

  if (!feedback || !visible) {
    return null;
  }

  const isCacheHit = feedback.cached;
  const icon = isCacheHit ? <Zap className="h-4 w-4" aria-hidden="true" /> : <Clock3 className="h-4 w-4" aria-hidden="true" />;
  const title = isCacheHit ? 'Smart Cache Hit' : 'Fresh Parse Completed';
  const subtitle = isCacheHit
    ? `Parsed in ${formatProcessingTime(feedback.processingTimeSeconds)}`
    : `Processed in ${formatProcessingTime(feedback.processingTimeSeconds)}`;

  if (variant === 'badge') {
    return (
      <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold ring-1 ${
        isCacheHit
          ? 'bg-emerald-50 text-emerald-700 ring-emerald-200'
          : 'bg-blue-50 text-blue-700 ring-blue-200'
      }`}>
        {icon}
        <span>{subtitle}</span>
      </div>
    );
  }

  return (
    <div
      aria-live="polite"
      className="fixed bottom-5 right-5 z-50 w-[min(24rem,calc(100vw-2rem))] rounded-3xl border border-slate-200 bg-white p-4 shadow-2xl"
      role="status"
    >
      <div className="flex items-start gap-3">
        <div className={`mt-1 rounded-full p-2 ${isCacheHit ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'}`}>
          {isCacheHit ? <Zap className="h-4 w-4" aria-hidden="true" /> : <Cpu className="h-4 w-4" aria-hidden="true" />}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <p className="font-semibold text-slate-900">{title}</p>
            <CheckCircle2 className="h-4 w-4 text-emerald-500" aria-hidden="true" />
          </div>
          <p className="mt-1 text-sm text-slate-600">{subtitle}</p>
          <p className="mt-1 truncate text-xs text-slate-500">{feedback.fileName}</p>
        </div>
        <button
          aria-label="Dismiss upload feedback"
          className="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
          onClick={() => {
            setVisible(false);
            clearFeedback();
          }}
          type="button"
        >
          ×
        </button>
      </div>
    </div>
  );
}

export default SmartCacheIndicator;
