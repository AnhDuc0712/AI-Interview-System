import { useMutation, useQueryClient } from '@tanstack/react-query';

import { useAppAuth } from '../../auth/AuthProvider';
import { useAppStore } from '../../../shared/store/useAppStore';
import { uploadCV } from '../api/cvApi';

type UploadCVVariables = {
  file: File;
  onProgress?: (progress: number) => void;
};

export const useUploadCV = () => {
  const auth = useAppAuth();
  const queryClient = useQueryClient();
  const setLastUploadFeedback = useAppStore((state) => state.setLastUploadFeedback);

  return useMutation({
    mutationFn: ({ file, onProgress }: UploadCVVariables) => uploadCV(auth.getToken, file, onProgress),
    onSuccess: (response) => {
      setLastUploadFeedback({
        cached: Boolean(response.cached),
        processingTimeSeconds: response.processing_time_seconds ?? null,
        fileName: response.cv.original_file.original_filename,
        uploadedAt: Date.now()
      });
      queryClient.invalidateQueries({ queryKey: ['cvs'] });
      queryClient.invalidateQueries({ queryKey: ['profile', 'me'] });
    }
  });
};
