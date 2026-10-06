import React from 'react';
import { BookOpen, Layers } from 'lucide-react';
import { Summary } from '../../types';
import { Card } from '../common/Card';

interface DetailedBreakdownProps {
  summary?: Summary | null;
}

export const DetailedBreakdown: React.FC<DetailedBreakdownProps> = ({ summary }) => {
  if (!summary?.detailed_summary) {
    return (
      <Card className="flex flex-col items-center justify-center py-16 text-center">
        <Layers className="w-10 h-10 text-slate-600 mb-3" />
        <h3 className="text-base font-semibold text-slate-300">Detailed breakdown not yet available</h3>
        <p className="text-xs text-slate-500 max-w-sm mt-1">
          Detailed concepts and section breakdowns will appear here once analysis finishes.
        </p>
      </Card>
    );
  }

  return (
    <Card className="space-y-6">
      <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
        <div className="w-8 h-8 rounded-lg bg-brand-500/10 text-brand-400 flex items-center justify-center">
          <BookOpen className="w-4 h-4" />
        </div>
        <div>
          <h2 className="text-base font-bold text-white">Comprehensive Educational Breakdown</h2>
          <p className="text-xs text-slate-400">Structured chapters, deep dives, and key insights</p>
        </div>
      </div>

      <div className="prose prose-invert max-w-none text-slate-200 text-sm sm:text-base leading-relaxed space-y-4">
        {summary.detailed_summary.split('\n\n').map((paragraph, idx) => {
          if (paragraph.startsWith('### ')) {
            return (
              <h3 key={idx} className="text-lg font-bold text-brand-300 pt-3 pb-1 border-b border-slate-800/60">
                {paragraph.replace('### ', '')}
              </h3>
            );
          }
          if (paragraph.startsWith('## ')) {
            return (
              <h2 key={idx} className="text-xl font-extrabold text-white pt-4 pb-2 border-b border-slate-800">
                {paragraph.replace('## ', '')}
              </h2>
            );
          }
          if (paragraph.startsWith('- ') || paragraph.startsWith('* ')) {
            return (
              <ul key={idx} className="list-disc list-inside space-y-1 text-slate-300 pl-2">
                {paragraph.split('\n').map((line, lIdx) => (
                  <li key={lIdx}>{line.replace(/^[-*]\s*/, '')}</li>
                ))}
              </ul>
            );
          }
          return (
            <p key={idx} className="text-slate-300 leading-relaxed">
              {paragraph}
            </p>
          );
        })}
      </div>
    </Card>
  );
};
