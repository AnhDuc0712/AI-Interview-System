import { useQuery } from '@tanstack/react-query';
import { fetchJson } from '../api/apiClient';

type HealthResponse = {
  status: string;
  database: boolean;
};

export const useHealthQuery = () => {
  return useQuery<HealthResponse, Error>({
    queryKey: ['health'],
    queryFn: () => fetchJson('/health')
  });
};
