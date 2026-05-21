import {
  fetchAuthenticatedJson,
  type TokenProvider,
  uploadAuthenticatedFileWithMeta
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
  const response = await uploadAuthenticatedFileWithMeta<CVUploadResponse>({
    path: '/cvs/upload',
    file,
    getToken,
    onProgress
  });

  const body = response.data;
  const cachedHeader = response.meta.headers['x-smart-cache-hit'] ?? response.meta.headers['x-cache-hit'];
  const processingSecondsHeader =
    response.meta.headers['x-processing-time-seconds'] ?? response.meta.headers['x-processing-duration-seconds'];

  return {
    ...body,
    cached: body.cached ?? cachedHeader === 'true',
    processing_time_seconds:
      body.processing_time_seconds ??
      (processingSecondsHeader ? Number(processingSecondsHeader) : null)
  };
};
