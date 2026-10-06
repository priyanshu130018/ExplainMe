import React from 'react';
import { Video, Zap, Sparkles } from 'lucide-react';
import { Card } from '../common/Card';

interface StatsOverviewProps {
  totalVideos: number;
}

export const StatsOverview: React.FC<StatsOverviewProps> = ({ totalVideos }) => {
  const stats = [
    {
      label: 'Videos Analyzed',
      value: totalVideos.toString(),
      icon: <Video className="w-5 h-5 text-brand-400" />,
      bg: 'bg-brand-500/10',
    },
    {
      label: 'Average Speed',
      value: '< 5 sec',
      icon: <Zap className="w-5 h-5 text-amber-400" />,
      bg: 'bg-amber-500/10',
    },
    {
      label: 'AI Tutoring Mode',
      value: 'Grounded RAG',
      icon: <Sparkles className="w-5 h-5 text-emerald-400" />,
      bg: 'bg-emerald-500/10',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {stats.map((stat, i) => (
        <Card key={i} className="flex items-center gap-4 p-5">
          <div className={`w-12 h-12 rounded-2xl ${stat.bg} flex items-center justify-center shrink-0`}>
            {stat.icon}
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{stat.label}</p>
            <p className="text-xl font-extrabold text-white mt-0.5">{stat.value}</p>
          </div>
        </Card>
      ))}
    </div>
  );
};
