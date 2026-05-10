import { useMemo, useState } from 'react';

import type { ApiError } from '../../../shared/api/apiClient';
import { useUploadCV } from '../hooks/useUploadCV';
import CVUploadDropzone from './CVUploadDropzone';
import UploadProgress from './UploadProgress';

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;

type CVUploadCardProps = {
  onSuccess?: (publicId: string) => void;
};

const CVUploadCard = ({ onSuccess }: CVUploadCardProps) => {
  const uploadMutation = useUploadCV();
  const [progress, setProgress] = useState(0);
  const [localError, setLocalError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const remoteError = useMemo(() => {
    const error = uploadMutation.error as ApiError | null;
    return error?.message ?? null;
  }, [uploadMutation.error]);

  const validateFile = (file: File) => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    if (!extension || !['pdf', 'docx'].includes(extension)) {
      return 'Please upload a PDF or DOCX file.';
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      return 'This file is too large. Please upload a file under 5MB.';
    }
    return null;
  };

  const handleUpload = async (file: File) => {
    const validationMessage = validateFile(file);
    setLocalError(validationMessage);
    setSuccessMessage(null);
    if (validationMessage) {
      return;
    }

    try {
      setLocalError(null);
      setProgress(0);
      const response = await uploadMutation.mutateAsync({
        file,
        onProgress: setProgress
      });
      setProgress(100);
      setSuccessMessage(`${response.cv.original_file.original_filename} was parsed successfully.`);
      onSuccess?.(response.cv.public_id);
    } catch {
      setProgress(0);
    }
  };

  return (
    <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-5">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">CV Upload</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">Bring your resume into the workspace</h2>
          <p className="mt-2 text-sm text-slate-500">
            Upload once, track parsing, and keep every version available for future interview workflows.
          </p>
        </div>
        <CVUploadDropzone
          disabled={uploadMutation.isPending}
          error={localError ?? remoteError}
          onFileSelect={(file) => {
            void handleUpload(file);
          }}
        />
        {uploadMutation.isPending ? (
          <UploadProgress progress={progress} statusLabel="Uploading and parsing your CV" />
        ) : null}
        {successMessage ? (
          <div className="rounded-2xl bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700">
            {successMessage}
          </div>
        ) : null}
      </div>
    </section>
  );
};

export default CVUploadCard;
