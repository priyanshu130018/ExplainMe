import React from 'react';
import { Lightbulb, PlayCircle } from 'lucide-react';
import { KeyPoint } from '../../types';
import { formatSecondsToTimestamp } from '../../lib/utils';
import { Card } from '../common/Card';

interface KeyTakeawaysProps {
  keyPoints: KeyPoint[];
  onTimestampClick?: (seconds: number) => void;
}

export const KeyTakeaways: React.FC<KeyTakeawaysProps> = ({ keyPoints, onTimestampClick }) => {
  if (!keyPoints || keyPoints.length === 0) {
    return (
      <Card className="flex flex-col items-center justify-center py-12 text-center">
        <Lightbulb className="w-10 h-10 text-slate-600 mb-3" />
        <h3 className="text-base font-semibold text-slate-300">No key takeaways extracted yet</h3>
        <p className="text-xs text-slate-500 max-w-sm mt-1">
          Key points and actionable takeaways will appear as soon as processing completes.
        </p>
      </Card>
    );
  }

  return (
    <Card className="space-y-4">
      <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
        <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
          <Lightbulb className="w-4 h-4" />
        </div>
        <div>
          <h2 className="text-base font-bold text-white">Key Ideas & Insights</h2>
          <p className="text-xs text-slate-400">Core concepts extracted from the video</p>
        </div>
      </div>

      <div className="space-y-3">
        {keyPoints.map((point, index) => (
          <div
            key={point.id || index}
            className="flex items-start gap-3.5 p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 hover:border-slate-700 transition-colors group"
          >
            <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-brand-500/10 text-brand-400 border border-brand-500/20 flex items-center justify-center text-xs font-bold mt-0.5">
              {point.point_index || index + 1}
            </span>

            <div className="flex-1 space-y-1">
              <div className="flex items-center justify-between gap-2">
                <h4 className="text-sm font-semibold text-white group-hover:text-brand-300 transition-colors">
                  {point.title}
                </h4>
                {point.timestamp_seconds !== null && point.timestamp_seconds !== undefined && (
                  <button
                    onClick={() => onTimestampClick && onTimestampClick(point.timestamp_seconds!)}
                    className="flex items-center gap-1 text-[11px] font-mono font-medium px-2 py-0.5 rounded-md bg-slate-800 text-brand-300 hover:bg-brand-600/30 transition-colors"
                    title="Jump to video timestamp"
                  >
                    <PlayCircle className="w-3 h-3" />
                    <span>{formatSecondsToTimestamp(point.timestamp_seconds)}</span>
                  </button>
                )}
              </div>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                {point.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
