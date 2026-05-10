type UploadProgressProps = {
  progress: number;
  statusLabel: string;
};

const UploadProgress = ({ progress, statusLabel }: UploadProgressProps) => (
  <div className="space-y-2">
    <div className="flex items-center justify-between text-sm text-slate-600">
      <span>{statusLabel}</span>
      <span>{progress}%</span>
    </div>
    <div className="h-2 overflow-hidden rounded-full bg-slate-100">
      <div
        className="h-full rounded-full bg-blue-600 transition-all duration-200"
        style={{ width: `${progress}%` }}
      />
    </div>
  </div>
);

export default UploadProgress;
