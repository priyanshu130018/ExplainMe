import { apiClient } from './client';
import { AnalysisJob } from '../types';
import { HealthCheckResponse } from '../types/api';

export const jobApi = {
  getStatus: (jobId: string): Promise<AnalysisJob> => {
    return apiClient.get<AnalysisJob>(`/jobs/${jobId}`);
  },
};

export const healthApi = {
  check: (): Promise<HealthCheckResponse> => {
    return apiClient.get<HealthCheckResponse>('/health');
  },
};
