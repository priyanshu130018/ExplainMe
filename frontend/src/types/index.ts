export type JobStatus = 
  | 'queued' 
  | 'downloading' 
  | 'transcribing' 
  | 'summarizing' 
  | 'indexing' 
  | 'completed' 
  | 'failed';

export interface AnalysisJob {
  id: string;
  video_id: string;
  status: JobStatus;
  progress_percent: number;
  current_step: string;
  source_used?: string | null;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Summary {
  id: string;
  video_id: string;
  quick_summary: string;
  detailed_summary: string;
  model_used: string;
  language: string;
}

export interface KeyPoint {
  id?: string;
  point_index: number;
  title: string;
  description: string;
  timestamp_seconds?: number | null;
}

export interface Keyword {
  id?: string;
  keyword: string;
  category?: string | null;
  relevance_score?: number | null;
}

export interface TranscriptChunk {
  id: string;
  chunk_index: number;
  start_time: number;
  end_time: number;
  text: string;
}

export interface Transcript {
  id: string;
  video_id: string;
  full_text: string;
  language: string;
  source_type: string;
  word_count: number;
  chunks: TranscriptChunk[];
}

export interface VideoListItem {
  id: string;
  youtube_id: string;
  url: string;
  title: string;
  channel_name?: string | null;
  duration_seconds?: number | null;
  thumbnail_url?: string | null;
  view_count?: number | null;
  language_code: string;
  created_at: string;
  updated_at: string;
  latest_job_status?: JobStatus | null;
  quick_summary_preview?: string | null;
}

export interface VideoDetail {
  id: string;
  youtube_id: string;
  url: string;
  title: string;
  channel_name?: string | null;
  duration_seconds?: number | null;
  thumbnail_url?: string | null;
  view_count?: number | null;
  language_code: string;
  created_at: string;
  updated_at: string;
  summary?: Summary | null;
  key_points: KeyPoint[];
  keywords: Keyword[];
  transcript_preview?: string | null;
  transcript_word_count?: number | null;
  latest_job?: AnalysisJob | null;
}

export interface QuestionAnswer {
  id: string;
  video_id: string;
  question: string;
  answer: string;
  sources?: Record<string, any> | null;
  created_at: string;
}
