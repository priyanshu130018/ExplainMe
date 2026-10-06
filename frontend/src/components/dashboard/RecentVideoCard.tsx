import React from 'react';
import { Link } from 'react-router-dom';
import { Play, CheckCircle2, Loader2, AlertCircle } from 'lucide-react';
import { VideoListItem } from '../../types';
import { formatDuration, formatDate } from '../../lib/utils';

interface RecentVideoCardProps {
  video: VideoListItem;
}

export const RecentVideoCard: React.FC<RecentVideoCardProps> = ({ video }) => {
  const isProcessing = video.latest_job_status && ['queued', 'downloading', 'transcribing', 'summarizing', 'indexing', 'processing'].includes(video.latest_job_status);

  return (
    <Link
      to={`/video/${video.id}`}
      className="group flex flex-col justify-between glass-panel rounded-2xl p-4 sm:p-5 border border-slate-800 hover:border-brand-500/40 hover:bg-slate-900/90 transition-all duration-300 hover:shadow-xl hover:shadow-brand-500/5"
    >
      <div className="space-y-3.5">
        {/* Thumbnail preview */}
        <div className="relative aspect-video rounded-xl overflow-hidden bg-slate-900 border border-slate-800/80 group-hover:border-slate-700 transition-colors">
          {video.thumbnail_url ? (
            <img
              src={video.thumbnail_url}
              alt={video.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-slate-900 text-slate-700">
              <Play className="w-8 h-8" />
            </div>
          )}

          {video.duration_seconds && (
            <span className="absolute bottom-2 right-2 bg-slate-950/80 backdrop-blur text-[11px] font-mono px-2 py-0.5 rounded-md text-slate-200">
              {formatDuration(video.duration_seconds)}
            </span>
          )}

          {isProcessing && (
            <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center gap-2 text-brand-300 text-xs font-semibold">
              <Loader2 className="w-4 h-4 animate-spin text-brand-400" />
              <span>Analyzing...</span>
            </div>
          )}
        </div>

        {/* Title and metadata */}
        <div>
          <div className="flex items-center justify-between gap-2 mb-1.5">
            <span className="text-xs font-medium text-brand-400 truncate max-w-[70%]">
              {video.channel_name || 'YouTube'}
            </span>
            <span className="text-[11px] text-slate-500">{formatDate(video.created_at)}</span>
          </div>

          <h3 className="text-sm font-bold text-white group-hover:text-brand-300 transition-colors line-clamp-2 leading-snug">
            {video.title}
          </h3>

          {video.quick_summary_preview && (
            <p className="text-xs text-slate-400 line-clamp-2 mt-2 leading-relaxed">
              {video.quick_summary_preview}
            </p>
          )}
        </div>
      </div>

      {/* Footer status */}
      <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between mt-3 text-xs">
        {video.latest_job_status === 'completed' && (
          <span className="flex items-center gap-1 text-emerald-400 text-[11px] font-medium">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Ready</span>
          </span>
        )}
        {isProcessing && (
          <span className="flex items-center gap-1 text-amber-400 text-[11px] font-medium">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span>In progress</span>
          </span>
        )}
        {video.latest_job_status === 'failed' && (
          <span className="flex items-center gap-1 text-red-400 text-[11px] font-medium">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Failed</span>
          </span>
        )}
        <span className="text-brand-400 text-[11px] font-semibold group-hover:translate-x-0.5 transition-transform">
          View insights →
        </span>
      </div>
    </Link>
  );
};
