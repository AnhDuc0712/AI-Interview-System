import { useMutation, useQueryClient } from '@tanstack/react-query';

import { useAppAuth } from '../../auth/AuthProvider';
import { uploadCV } from '../api/cvApi';

type UploadCVVariables = {
  file: File;
  onProgress?: (progress: number) => void;
};

export const useUploadCV = () => {
  const auth = useAppAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, onProgress }: UploadCVVariables) => uploadCV(auth.getToken, file, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cvs'] });
      queryClient.invalidateQueries({ queryKey: ['profile', 'me'] });
    }
  });
};
