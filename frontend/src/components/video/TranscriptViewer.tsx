import React, { useState } from 'react';
import { Search, FileText, Play, Copy, Check } from 'lucide-react';
import { Transcript } from '../../types';
import { formatSecondsToTimestamp } from '../../lib/utils';
import { Card } from '../common/Card';

interface TranscriptViewerProps {
  transcript?: Transcript | null;
  previewText?: string | null;
  onTimestampClick?: (seconds: number) => void;
}

export const TranscriptViewer: React.FC<TranscriptViewerProps> = ({
  transcript,
  previewText,
  onTimestampClick,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [copied, setCopied] = useState(false);

  const fullText = transcript?.full_text || previewText || '';

  const handleCopy = () => {
    if (!fullText) return;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const chunks = transcript?.chunks || [];
  const filteredChunks = searchQuery
    ? chunks.filter((c) => c.text.toLowerCase().includes(searchQuery.toLowerCase()))
    : chunks;

  if (!fullText) {
    return (
      <Card className="flex flex-col items-center justify-center py-16 text-center">
        <FileText className="w-10 h-10 text-slate-600 mb-3" />
        <h3 className="text-base font-semibold text-slate-300">Transcript not available</h3>
        <p className="text-xs text-slate-500 max-w-sm mt-1">
          The transcript will appear here once audio extraction/caption fetching finishes.
        </p>
      </Card>
    );
  }

  return (
    <Card className="space-y-4">
      {/* Header with Search and Copy */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Full Video Transcript</h2>
            <p className="text-xs text-slate-400">
              {transcript?.word_count || fullText.split(' ').length} words • {transcript?.source_type || 'captions'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {chunks.length > 0 && (
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search transcript..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-slate-900 border border-slate-700/80 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 w-40 sm:w-56"
              />
            </div>
          )}

          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {/* Timestamped chunks list or text preview */}
      {chunks.length > 0 ? (
        <div className="max-h-[500px] overflow-y-auto space-y-2 pr-2">
          {filteredChunks.length > 0 ? (
            filteredChunks.map((chunk) => (
              <div
                key={chunk.id || chunk.chunk_index}
                className="flex items-start gap-3 p-2.5 rounded-xl hover:bg-slate-900/90 transition-colors group"
              >
                <button
                  onClick={() => onTimestampClick && onTimestampClick(chunk.start_time)}
                  className="shrink-0 flex items-center gap-1 text-[11px] font-mono font-medium px-2 py-1 rounded bg-slate-800/80 text-brand-400 hover:bg-brand-600/20 transition-colors mt-0.5"
                >
                  <Play className="w-2.5 h-2.5 fill-current" />
                  <span>{formatSecondsToTimestamp(chunk.start_time)}</span>
                </button>
                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed pt-0.5">
                  {chunk.text}
                </p>
              </div>
            ))
          ) : (
            <p className="text-center py-8 text-xs text-slate-500">
              No matching lines found for "{searchQuery}".
            </p>
          )}
        </div>
      ) : (
        <div className="max-h-[400px] overflow-y-auto p-4 rounded-xl bg-slate-900/60 border border-slate-800/60 text-xs sm:text-sm leading-relaxed text-slate-300 whitespace-pre-wrap">
          {fullText}
        </div>
      )}
    </Card>
  );
};
