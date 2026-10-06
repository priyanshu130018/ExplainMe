import React from 'react';
import { Tag } from 'lucide-react';
import { Keyword } from '../../types';
import { Card } from '../common/Card';

interface KeywordPillsProps {
  keywords: Keyword[];
}

export const KeywordPills: React.FC<KeywordPillsProps> = ({ keywords }) => {
  if (!keywords || keywords.length === 0) return null;

  return (
    <Card className="space-y-3">
      <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
        <Tag className="w-4 h-4 text-brand-400" />
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">Topics & Keywords</h3>
      </div>

      <div className="flex flex-wrap gap-2">
        {keywords.map((kw, i) => (
          <div
            key={kw.id || i}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700/60 text-xs font-medium text-slate-200 hover:border-brand-500/40 hover:text-brand-300 transition-colors"
          >
            <span>{kw.keyword}</span>
            {kw.category && (
              <span className="text-[10px] text-slate-400 bg-slate-900/90 px-1.5 py-0.5 rounded">
                {kw.category}
              </span>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
};
