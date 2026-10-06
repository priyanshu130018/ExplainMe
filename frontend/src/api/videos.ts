import { apiClient } from './client';
import { 
  AnalyzeVideoRequest, 
  AnalyzeVideoResponse, 
  VideoListResponse, 
  AskQuestionRequest,
} from '../types/api';
import { VideoDetail, Transcript, Summary, QuestionAnswer } from '../types';

export const videoApi = {
  analyze: (data: AnalyzeVideoRequest): Promise<AnalyzeVideoResponse> => {
    return apiClient.post<AnalyzeVideoResponse>('/videos/analyze', data);
  },

  list: (page = 1, pageSize = 20): Promise<VideoListResponse> => {
    return apiClient.get<VideoListResponse>(`/videos?page=${page}&page_size=${pageSize}`);
  },

  getById: (videoId: string): Promise<VideoDetail> => {
    return apiClient.get<VideoDetail>(`/videos/${videoId}`);
  },

  getTranscript: (videoId: string): Promise<Transcript> => {
    return apiClient.get<Transcript>(`/videos/${videoId}/transcript`);
  },

  getSummary: (videoId: string): Promise<Summary> => {
    return apiClient.get<Summary>(`/videos/${videoId}/summary`);
  },

  askQuestion: (videoId: string, data: AskQuestionRequest): Promise<QuestionAnswer> => {
    return apiClient.post<QuestionAnswer>(`/videos/${videoId}/ask`, data);
  },
};
