import React from 'react';
import { Video, PlusCircle, ArrowRight } from 'lucide-react';
import { AnalyzeForm } from '../components/dashboard/AnalyzeForm';
import { RecentVideoCard } from '../components/dashboard/RecentVideoCard';
import { StatsOverview } from '../components/dashboard/StatsOverview';
import { useRecentVideos } from '../hooks/useRecentVideos';
import { Skeleton } from '../components/common/Skeleton';
import { Card } from '../components/common/Card';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { data, isLoading, error } = useRecentVideos(1, 12);

  const items = data?.items || [];
  const total = data?.total || 0;

  return (
    <div className="space-y-8">
      {/* Top Banner / Ingestion Box */}
      <div className="space-y-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Video Analysis Studio
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Submit a YouTube URL to extract summaries, key insights, and conversational Q&A.
          </p>
        </div>

        <AnalyzeForm />
      </div>

      {/* Stats Bar */}
      <StatsOverview totalVideos={total} />

      {/* Recent Videos Section */}
      <div className="space-y-4 pt-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Video className="w-5 h-5 text-brand-400" />
            <h2 className="text-lg font-bold text-white">Recent Analyses</h2>
          </div>
          {items.length > 0 && (
            <Link
              to="/history"
              className="text-xs font-semibold text-brand-400 hover:text-brand-300 flex items-center gap-1 transition-colors"
            >
              <span>View all ({total})</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          )}
        </div>

        {/* Loading Skeletons */}
        {isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="space-y-3 p-4">
                <Skeleton className="aspect-video w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </Card>
            ))}
          </div>
        )}

        {/* Error State */}
        {error && (
          <Card className="p-8 text-center text-red-300 border-red-800/40 bg-red-950/20 text-xs">
            <p className="font-semibold">Unable to fetch recent videos</p>
            <p className="text-red-400/80 mt-1">{error.message}</p>
          </Card>
        )}

        {/* Empty State */}
        {!isLoading && !error && items.length === 0 && (
          <Card className="flex flex-col items-center justify-center py-16 text-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500">
              <PlusCircle className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">No videos analyzed yet</h3>
              <p className="text-xs text-slate-400 max-w-sm mt-1">
                Paste a YouTube URL in the box above to generate your first AI video breakdown!
              </p>
            </div>
          </Card>
        )}

        {/* Video Grid */}
        {!isLoading && items.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((video) => (
              <RecentVideoCard key={video.id} video={video} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
