import React from 'react';
import { Clock, Eye, User, AlertCircle, CheckCircle2, Loader2, ExternalLink } from 'lucide-react';
import { VideoDetail, AnalysisJob } from '../../types';
import { formatDuration } from '../../lib/utils';
import { Badge } from '../common/Badge';

interface VideoHeroProps {
  video: VideoDetail;
  job?: AnalysisJob | null;
  seekTime?: number | null;
}

export const VideoHero: React.FC<VideoHeroProps> = ({ video, job, seekTime }) => {
  const isProcessing = job && ['queued', 'downloading', 'transcribing', 'summarizing', 'indexing', 'processing'].includes(job.status);
  const isFailed = job && job.status === 'failed';

  const embedSrc = seekTime !== null && seekTime !== undefined && seekTime > 0
    ? `https://www.youtube-nocookie.com/embed/${video.youtube_id}?start=${Math.floor(seekTime)}&autoplay=1`
    : `https://www.youtube-nocookie.com/embed/${video.youtube_id}`;

  const getStatusBadge = () => {
    if (!job) return null;
    if (job.status === 'completed') {
      return (
        <Badge variant="success" className="gap-1">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Analyzed</span>
        </Badge>
      );
    }
    if (isProcessing) {
      return (
        <Badge variant="warning" className="gap-1 animate-pulse">
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          <span>{job.status}</span>
        </Badge>
      );
    }
    if (isFailed) {
      return (
        <Badge variant="danger" className="gap-1">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>Failed</span>
        </Badge>
      );
    }
    return <Badge variant="default">{job.status}</Badge>;
  };

  return (
    <div className="glass-panel rounded-3xl p-6 sm:p-8 relative overflow-hidden border border-slate-800">
      {/* Background ambient lighting */}
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-brand-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start relative z-10">
        {/* Left: Video Embed / Thumbnail */}
        <div className="lg:col-span-5 w-full">
          <div className="relative aspect-video rounded-2xl overflow-hidden border border-slate-700/80 bg-slate-900 shadow-2xl group">
            <iframe
              key={seekTime || 'initial'}
              src={embedSrc}
              title={video.title}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              className="w-full h-full border-0"
            />
          </div>
        </div>

        {/* Right: Metadata and Processing Status */}
        <div className="lg:col-span-7 flex flex-col justify-between h-full space-y-4">
          <div>
            <div className="flex flex-wrap items-center gap-2.5 mb-3">
              {getStatusBadge()}
              {job?.source_used && (
                <Badge variant="purple">Source: {job.source_used}</Badge>
              )}
              <Badge variant="default">{video.language_code.toUpperCase()}</Badge>
            </div>

            <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-white tracking-tight leading-snug mb-3">
              {video.title}
            </h1>

            <div className="flex flex-wrap items-center gap-y-2 gap-x-5 text-xs sm:text-sm text-slate-400">
              {video.channel_name && (
                <div className="flex items-center gap-1.5 font-medium text-slate-300">
                  <User className="w-4 h-4 text-brand-400" />
                  <span>{video.channel_name}</span>
                </div>
              )}
              {video.duration_seconds && (
                <div className="flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-slate-500" />
                  <span>{formatDuration(video.duration_seconds)}</span>
                </div>
              )}
              {video.view_count && (
                <div className="flex items-center gap-1.5">
                  <Eye className="w-4 h-4 text-slate-500" />
                  <span>{video.view_count.toLocaleString()} views</span>
                </div>
              )}
              <a
                href={video.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-brand-400 hover:text-brand-300 transition-colors ml-auto font-medium"
              >
                <span>Watch on YouTube</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
