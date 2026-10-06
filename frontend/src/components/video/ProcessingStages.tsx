import React from 'react';
import { CheckCircle2, Circle, Loader2, AlertCircle } from 'lucide-react';
import { AnalysisJob } from '../../types';
import { Card } from '../common/Card';

interface ProcessingStagesProps {
  job: AnalysisJob;
}

export const ProcessingStages: React.FC<ProcessingStagesProps> = ({ job }) => {
  const progress = job.progress_percent || 0;
  const isFailed = job.status === 'failed';

  const stages = [
    { label: 'Getting video details & metadata', minProgress: 15 },
    { label: 'Retrieving captions & speech transcript', minProgress: 35 },
    { label: 'Normalizing & segmenting transcript', minProgress: 50 },
    { label: 'Generating quick & detailed explanations', minProgress: 65 },
    { label: 'Extracting key takeaways & keywords', minProgress: 80 },
    { label: 'Indexing vector knowledge base for Q&A', minProgress: 90 },
    { label: 'Finalizing knowledge assets', minProgress: 98 },
  ];

  return (
    <Card className="border-brand-500/30 bg-gradient-to-br from-slate-900 via-slate-900/90 to-brand-950/30 p-6 sm:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-brand-500/10 text-brand-400 border border-brand-500/20 flex items-center justify-center">
            <Loader2 className="w-5 h-5 animate-spin" />
          </div>
          <div>
            <h3 className="text-base sm:text-lg font-bold text-white">AI Video Intelligence Pipeline</h3>
            <p className="text-xs text-slate-400">{job.current_step || 'Processing video...'}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <span className="text-2xl font-black text-brand-400 font-mono">{progress}%</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden p-0.5">
        <div
          className="h-full bg-gradient-to-r from-brand-600 via-indigo-500 to-emerald-400 rounded-full transition-all duration-700 ease-out"
          style={{ width: `${Math.max(progress, 5)}%` }}
        />
      </div>

      {/* Stages Checklist */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
        {stages.map((st, i) => {
          const isDone = progress >= st.minProgress;
          const isCurrent = progress < st.minProgress && (i === 0 || progress >= stages[i - 1].minProgress);

          return (
            <div
              key={i}
              className={`flex items-center gap-2.5 p-2.5 rounded-xl border text-xs transition-colors ${
                isDone
                  ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-300 font-medium'
                  : isCurrent
                  ? 'bg-brand-950/40 border-brand-500/40 text-brand-200 font-semibold shadow-sm'
                  : 'bg-slate-900/40 border-slate-800/60 text-slate-500'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : isCurrent ? (
                <Loader2 className="w-4 h-4 animate-spin text-brand-400 shrink-0" />
              ) : (
                <Circle className="w-4 h-4 text-slate-600 shrink-0" />
              )}
              <span className="truncate">{st.label}</span>
            </div>
          );
        })}
      </div>

      {isFailed && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800/40 text-red-200 text-xs flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-300">Processing Interrupted</p>
            <p className="text-red-400/90 mt-0.5">{job.error_message || 'An unexpected error occurred during pipeline execution.'}</p>
          </div>
        </div>
      )}
    </Card>
  );
};
