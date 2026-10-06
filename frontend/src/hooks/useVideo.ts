import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { videoApi } from '../api/videos';
import { VideoDetail, Transcript } from '../types';
import { AnalyzeVideoRequest, AskQuestionRequest } from '../types/api';

export function useVideo(videoId?: string) {
  return useQuery<VideoDetail, Error>({
    queryKey: ['video', videoId],
    queryFn: () => {
      if (!videoId) throw new Error('Video ID is required');
      return videoApi.getById(videoId);
    },
    enabled: !!videoId,
  });
}

export function useVideoTranscript(videoId?: string) {
  return useQuery<Transcript, Error>({
    queryKey: ['video-transcript', videoId],
    queryFn: () => {
      if (!videoId) throw new Error('Video ID is required');
      return videoApi.getTranscript(videoId);
    },
    enabled: !!videoId,
  });
}

export function useAnalyzeVideoMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: AnalyzeVideoRequest) => videoApi.analyze(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recent-videos'] });
    },
  });
}

export function useAskQuestionMutation(videoId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: AskQuestionRequest) => videoApi.askQuestion(videoId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['video-qa', videoId] });
    },
  });
}
