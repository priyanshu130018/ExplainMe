import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Zap, 
  BookOpen, 
  Lightbulb, 
  FileText, 
  MessageSquare, 
  AlertCircle,
} from 'lucide-react';
import { useVideo, useVideoTranscript } from '../hooks/useVideo';
import { useAnalysisJob } from '../hooks/useAnalysisJob';
import { VideoHero } from '../components/video/VideoHero';
import { ProcessingStages } from '../components/video/ProcessingStages';
import { QuickExplanation } from '../components/video/QuickExplanation';
import { DetailedBreakdown } from '../components/video/DetailedBreakdown';
import { KeyTakeaways } from '../components/video/KeyTakeaways';
import { KeywordPills } from '../components/video/KeywordPills';
import { TranscriptViewer } from '../components/video/TranscriptViewer';
import { AskTutorSection } from '../components/video/AskTutorSection';
import { Tabs } from '../components/common/Tabs';
import { Skeleton } from '../components/common/Skeleton';
import { Card } from '../components/common/Card';

export const VideoDetailPage: React.FC = () => {
  const { videoId } = useParams<{ videoId: string }>();
  const [searchParams] = useSearchParams();
  const queryJobId = searchParams.get('job_id');

  const [activeTab, setActiveTab] = useState('overview');
  const [seekTime, setSeekTime] = useState<number | null>(null);

  const { data: video, isLoading: isVideoLoading, error: videoError, refetch: refetchVideo } = useVideo(videoId);
  
  const effectiveJobId = queryJobId || video?.latest_job?.id;
  const { data: job } = useAnalysisJob(effectiveJobId);
  const { data: transcript, refetch: refetchTranscript } = useVideoTranscript(videoId);

  const isProcessing = job && ['queued', 'downloading', 'transcribing', 'summarizing', 'indexing', 'processing'].includes(job.status);

  // If job completes, refetch the video and transcript
  useEffect(() => {
    if (job?.status === 'completed') {
      refetchVideo();
      refetchTranscript();
    }
  }, [job?.status, refetchVideo, refetchTranscript]);

  const handleTimestampClick = (seconds: number) => {
    setSeekTime(seconds);
    // Scroll window smoothly to video player if user is deep in tabs
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (isVideoLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-72 w-full rounded-3xl" />
        <Skeleton className="h-12 w-full rounded-2xl" />
        <Skeleton className="h-96 w-full rounded-2xl" />
      </div>
    );
  }

  if (videoError || !video) {
    return (
      <div className="space-y-4">
        <Link to="/dashboard" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Dashboard</span>
        </Link>
        <Card className="p-12 text-center text-red-300 border-red-800/40 bg-red-950/20">
          <AlertCircle className="w-10 h-10 mx-auto mb-3 text-red-400" />
          <h2 className="text-base font-bold">Video not found or failed to load</h2>
          <p className="text-xs text-red-400/80 mt-1">{videoError?.message || 'Video analysis record does not exist.'}</p>
        </Card>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Zap className="w-4 h-4" /> },
    { id: 'breakdown', label: 'Detailed Breakdown', icon: <BookOpen className="w-4 h-4" /> },
    { 
      id: 'insights', 
      label: 'Key Ideas', 
      icon: <Lightbulb className="w-4 h-4" />, 
      badge: video.key_points?.length || undefined 
    },
    { id: 'transcript', label: 'Transcript', icon: <FileText className="w-4 h-4" /> },
    { id: 'ask', label: 'Ask ExplainMe', icon: <MessageSquare className="w-4 h-4" /> },
  ];

  return (
    <div className="space-y-8">
      {/* Back button */}
      <Link
        to="/dashboard"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-brand-300 transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Dashboard</span>
      </Link>

      {/* Video Hero */}
      <VideoHero video={video} job={job || video.latest_job} seekTime={seekTime} />

      {/* Real-time Pipeline Processing Checklist UI */}
      {isProcessing && job && (
        <ProcessingStages job={job} />
      )}

      {/* Navigation Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      {/* Tab Panels */}
      <div className="space-y-6">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-8 space-y-6">
              <QuickExplanation summary={video.summary} />
              <KeyTakeaways keyPoints={video.key_points} onTimestampClick={handleTimestampClick} />
            </div>
            <div className="lg:col-span-4 space-y-6">
              <KeywordPills keywords={video.keywords} />
              <AskTutorSection
                videoId={video.id}
                hasTranscript={!!video.transcript_preview || !!transcript}
                onTimestampClick={handleTimestampClick}
              />
            </div>
          </div>
        )}

        {activeTab === 'breakdown' && (
          <DetailedBreakdown summary={video.summary} />
        )}

        {activeTab === 'insights' && (
          <KeyTakeaways keyPoints={video.key_points} onTimestampClick={handleTimestampClick} />
        )}

        {activeTab === 'transcript' && (
          <TranscriptViewer
            transcript={transcript}
            previewText={video.transcript_preview}
            onTimestampClick={handleTimestampClick}
          />
        )}

        {activeTab === 'ask' && (
          <AskTutorSection
            videoId={video.id}
            hasTranscript={!!video.transcript_preview || !!transcript}
            onTimestampClick={handleTimestampClick}
          />
        )}
      </div>
    </div>
  );
};
