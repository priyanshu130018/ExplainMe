import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Youtube, ArrowRight, AlertCircle } from 'lucide-react';
import { useAnalyzeVideoMutation } from '../../hooks/useVideo';
import { SAMPLE_VIDEOS } from '../../lib/constants';
import { Button } from '../common/Button';

interface AnalyzeFormProps {
  compact?: boolean;
  onSuccess?: (videoId: string, jobId: string) => void;
}

export const AnalyzeForm: React.FC<AnalyzeFormProps> = ({ compact = false, onSuccess }) => {
  const [url, setUrl] = useState('');
  const [language, setLanguage] = useState('english');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const navigate = useNavigate();
  const analyzeMutation = useAnalyzeVideoMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    const cleanUrl = url.trim();
    if (!cleanUrl) {
      setErrorMessage('Please enter a valid YouTube URL');
      return;
    }

    try {
      const response = await analyzeMutation.mutateAsync({
        url: cleanUrl,
        language,
      });

      if (onSuccess) {
        onSuccess(response.video_id, response.job_id);
      } else {
        navigate(`/video/${response.video_id}?job_id=${response.job_id}`);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to submit video for analysis.');
    }
  };

  const handleSampleClick = (sampleUrl: string) => {
    setUrl(sampleUrl);
    setErrorMessage(null);
  };

  return (
    <div className="w-full space-y-4">
      <form onSubmit={handleSubmit} className="relative group">
        <div className="glass-panel p-2 sm:p-2.5 rounded-2xl sm:rounded-3xl border border-slate-700/80 shadow-2xl flex flex-col sm:flex-row items-center gap-2">
          {/* URL Input */}
          <div className="relative flex-1 w-full flex items-center">
            <div className="absolute left-4 text-red-500 flex items-center">
              <Youtube className="w-5 h-5" />
            </div>
            <input
              type="text"
              placeholder="Paste any YouTube video link (e.g., https://www.youtube.com/watch?v=...)"
              value={url}
              onChange={(e) => {
                setUrl(e.target.value);
                if (errorMessage) setErrorMessage(null);
              }}
              className="w-full bg-transparent text-slate-100 placeholder-slate-500 text-sm sm:text-base pl-12 pr-4 py-3 rounded-xl focus:outline-none"
            />
          </div>

          {/* Language selector & Submit */}
          <div className="flex items-center gap-2 w-full sm:w-auto shrink-0 px-2 pb-2 sm:p-0">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-slate-900 border border-slate-700/80 text-slate-300 text-xs sm:text-sm rounded-xl px-3 py-3 focus:outline-none focus:border-brand-500 cursor-pointer"
            >
              <option value="english">English</option>
              <option value="hinglish">Hindi / Hinglish</option>
              <option value="auto">Auto-detect</option>
            </select>

            <Button
              type="submit"
              variant="primary"
              size={compact ? 'md' : 'lg'}
              isLoading={analyzeMutation.isPending}
              rightIcon={<ArrowRight className="w-4 h-4" />}
              className="w-full sm:w-auto"
            >
              <span>Explain</span>
            </Button>
          </div>
        </div>
      </form>

      {/* Error display */}
      {errorMessage && (
        <div className="flex items-center gap-2 p-3 rounded-xl bg-red-950/40 border border-red-800/40 text-red-300 text-xs animate-shake">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Sample video links for quick testing */}
      {!compact && (
        <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 pt-2 text-xs text-slate-400">
          <span className="font-semibold text-slate-500">Try an example:</span>
          {SAMPLE_VIDEOS.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSampleClick(sample.url)}
              className="px-2.5 py-1 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-brand-300 transition-colors"
            >
              {sample.title}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
