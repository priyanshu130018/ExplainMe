import React from 'react';
import { Zap, Copy, Check, BookOpen } from 'lucide-react';
import { Summary } from '../../types';
import { Card } from '../common/Card';

interface QuickExplanationProps {
  summary?: Summary | null;
}

export const QuickExplanation: React.FC<QuickExplanationProps> = ({ summary }) => {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    if (!summary?.quick_summary) return;
    navigator.clipboard.writeText(summary.quick_summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!summary?.quick_summary) {
    return (
      <Card className="flex flex-col items-center justify-center py-12 text-center">
        <BookOpen className="w-10 h-10 text-slate-600 mb-3" />
        <h3 className="text-base font-semibold text-slate-300">Quick explanation not yet generated</h3>
        <p className="text-xs text-slate-500 max-w-sm mt-1">
          Once video transcription completes, AI will generate a fast summary here.
        </p>
      </Card>
    );
  }

  return (
    <Card className="relative group border-brand-500/20 bg-gradient-to-br from-slate-900/90 to-slate-900/50">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
            <Zap className="w-4 h-4 fill-amber-400/20" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Quick Explanation</h2>
            <p className="text-xs text-slate-400">High-level 2-minute overview</p>
          </div>
        </div>

        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          title="Copy to clipboard"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>

      <p className="text-sm sm:text-base leading-relaxed text-slate-200 whitespace-pre-line font-normal">
        {summary.quick_summary}
      </p>
    </Card>
  );
};
