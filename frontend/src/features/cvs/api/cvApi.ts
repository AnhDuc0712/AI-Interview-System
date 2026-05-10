import {
  fetchAuthenticatedJson,
  type TokenProvider,
  uploadAuthenticatedFile
} from '../../../shared/api/apiClient';
import type { CVDetailResponse, CVListResponse, CVStatus, CVUploadResponse } from './types';

type ListMyCVsParams = {
  page?: number;
  limit?: number;
  status?: CVStatus | 'all';
};

export const listMyCVs = async (
  getToken: TokenProvider,
  params: ListMyCVsParams = {}
): Promise<CVListResponse> => {
  const searchParams = new URLSearchParams();
  searchParams.set('page', String(params.page ?? 1));
  searchParams.set('limit', String(params.limit ?? 10));
  if (params.status && params.status !== 'all') {
    searchParams.set('status', params.status);
  }

  return fetchAuthenticatedJson(`/cvs/me?${searchParams.toString()}`, getToken);
};

export const getCVDetail = async (
  getToken: TokenProvider,
  publicId: string
): Promise<CVDetailResponse> => {
  return fetchAuthenticatedJson(`/cvs/${publicId}`, getToken);
};

export const uploadCV = async (
  getToken: TokenProvider,
  file: File,
  onProgress?: (progress: number) => void
): Promise<CVUploadResponse> => {
  return uploadAuthenticatedFile({
    path: '/cvs/upload',
    file,
    getToken,
    onProgress
  });
};
