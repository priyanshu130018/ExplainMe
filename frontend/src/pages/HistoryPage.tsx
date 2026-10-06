import React, { useState } from 'react';
import { History, Search } from 'lucide-react';
import { useRecentVideos } from '../hooks/useRecentVideos';
import { RecentVideoCard } from '../components/dashboard/RecentVideoCard';
import { Skeleton } from '../components/common/Skeleton';
import { Card } from '../components/common/Card';

export const HistoryPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const { data, isLoading } = useRecentVideos(1, 50);

  const items = data?.items || [];
  const filtered = searchTerm
    ? items.filter(
        (v) =>
          v.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (v.channel_name && v.channel_name.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    : items;

  return (
    <div className="space-y-6">
      {/* Header & Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <History className="w-6 h-6 text-brand-400" />
            <h1 className="text-2xl font-bold text-white tracking-tight">Analysis History</h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Browse and review all previously analyzed YouTube videos.
          </p>
        </div>

        <div className="relative">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by title or channel..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-slate-900 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2 text-xs sm:text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 w-full sm:w-64"
          />
        </div>
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

      {/* Empty State */}
      {!isLoading && filtered.length === 0 && (
        <Card className="py-16 text-center text-slate-400 text-xs">
          <p className="font-semibold text-slate-300 text-sm">No videos found</p>
          <p className="mt-1">
            {searchTerm ? `No matches for "${searchTerm}".` : 'Analyze your first video to start building history!'}
          </p>
        </Card>
      )}

      {/* Videos Grid */}
      {!isLoading && filtered.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((video) => (
            <RecentVideoCard key={video.id} video={video} />
          ))}
        </div>
      )}
    </div>
  );
};
