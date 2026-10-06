import { useQuery } from '@tanstack/react-query';
import { videoApi } from '../api/videos';
import { VideoListResponse } from '../types/api';

export function useRecentVideos(page = 1, pageSize = 20) {
  return useQuery<VideoListResponse, Error>({
    queryKey: ['recent-videos', page, pageSize],
    queryFn: () => videoApi.list(page, pageSize),
    refetchInterval: 5000, // Refresh recent list periodically
  });
}
