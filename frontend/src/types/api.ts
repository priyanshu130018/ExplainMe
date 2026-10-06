import { VideoListItem } from './index';

export interface HealthCheckResponse {
  status: string;
  app_name: string;
  version: string;
  timestamp: string;
  services: {
    database?: { status: string; type?: string; error?: string };
    redis?: { status: string; error?: string };
  };
}

export interface AnalyzeVideoRequest {
  url: string;
  language?: string;
}

export interface AnalyzeVideoResponse {
  job_id: string;
  video_id: string;
  status: string;
  message: string;
}

export interface VideoListResponse {
  items: VideoListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface AskQuestionRequest {
  question: string;
}
