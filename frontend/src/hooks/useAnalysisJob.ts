import { useEffect, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { jobApi } from '../api/jobs';
import { AnalysisJob } from '../types';
import { API_BASE_URL } from '../lib/constants';

export function useAnalysisJob(jobId?: string | null) {
  const queryClient = useQueryClient();
  const [sseJob, setSseJob] = useState<AnalysisJob | null>(null);

  // TanStack Query polling fallback
  const query = useQuery<AnalysisJob, Error>({
    queryKey: ['job', jobId],
    queryFn: () => {
      if (!jobId) throw new Error('Job ID is required');
      return jobApi.getStatus(jobId);
    },
    enabled: !!jobId,
    refetchInterval: (q) => {
      const data = q.state.data;
      if (!data) return 1500;
      if (['queued', 'downloading', 'transcribing', 'summarizing', 'indexing', 'processing'].includes(data.status)) {
        return 1500;
      }
      return false;
    },
  });

  // Server-Sent Events (SSE) listener
  useEffect(() => {
    if (!jobId) return;

    let eventSource: EventSource | null = null;
    try {
      const url = `${API_BASE_URL}/jobs/${jobId}/events`;
      eventSource = new EventSource(url);

      eventSource.addEventListener('job.progress', (e: MessageEvent) => {
        try {
          const parsed = JSON.parse(e.data);
          setSseJob((prev) => ({
            ...(prev || ({} as AnalysisJob)),
            ...parsed,
          }));
          queryClient.setQueryData(['job', jobId], (old: any) => ({
            ...old,
            ...parsed,
          }));
        } catch {}
      });

      eventSource.addEventListener('job.completed', () => {
        queryClient.invalidateQueries({ queryKey: ['job', jobId] });
        queryClient.invalidateQueries({ queryKey: ['video'] });
        eventSource?.close();
      });

      eventSource.addEventListener('job.failed', () => {
        queryClient.invalidateQueries({ queryKey: ['job', jobId] });
        eventSource?.close();
      });

      eventSource.onerror = () => {
        // Close SSE on connection drop; TanStack polling will seamlessly take over
        eventSource?.close();
      };
    } catch {
      // Ignore SSE init errors and rely on query polling
    }

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [jobId, queryClient]);

  const activeData = sseJob || query.data;

  return {
    ...query,
    data: activeData,
  };
}
