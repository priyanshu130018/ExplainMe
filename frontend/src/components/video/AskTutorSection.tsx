import React, { useState } from 'react';
import { Send, Sparkles, Bot, User as UserIcon, Loader2, AlertCircle, PlayCircle } from 'lucide-react';
import { useAskQuestionMutation } from '../../hooks/useVideo';
import { formatSecondsToTimestamp } from '../../lib/utils';
import { Card } from '../common/Card';

interface SourceItem {
  chunk_index?: number;
  start_time: number;
  end_time: number;
  text_snippet?: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
  sources?: SourceItem[];
}

interface AskTutorSectionProps {
  videoId: string;
  hasTranscript: boolean;
  onTimestampClick?: (seconds: number) => void;
}

export const AskTutorSection: React.FC<AskTutorSectionProps> = ({
  videoId,
  hasTranscript,
  onTimestampClick,
}) => {
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      text: "Hello! I'm your ExplainMe AI Tutor for this video. Ask me any question, and I'll give you a grounded answer with exact video timestamps!",
    },
  ]);

  const askMutation = useAskQuestionMutation(videoId);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || askMutation.isPending) return;

    const userQ = question.trim();
    setQuestion('');
    setChatHistory((prev) => [...prev, { role: 'user', text: userQ }]);

    try {
      const res = await askMutation.mutateAsync({ question: userQ });
      const sourcesList: SourceItem[] = Array.isArray(res.sources)
        ? res.sources
        : [];

      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: res.answer,
          sources: sourcesList,
        },
      ]);
    } catch (err: any) {
      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: `Sorry, I couldn't process your question: ${err.message || 'Server error'}`,
        },
      ]);
    }
  };

  const sampleQuestions = [
    "What is the main conclusion of this video?",
    "Can you explain the key steps mentioned?",
    "What examples were used by the speaker?",
  ];

  return (
    <Card className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-brand-500/10 text-brand-400 flex items-center justify-center">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Ask ExplainMe Tutor</h2>
            <p className="text-xs text-slate-400">Grounded strictly in the video transcript</p>
          </div>
        </div>
      </div>

      {!hasTranscript ? (
        <div className="p-8 text-center text-slate-500 text-xs">
          <AlertCircle className="w-8 h-8 mx-auto mb-2 text-slate-600" />
          <p>Please wait until video analysis finishes to start asking questions.</p>
        </div>
      ) : (
        <>
          {/* Chat message history */}
          <div className="space-y-4 max-h-[460px] overflow-y-auto pr-1">
            {chatHistory.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-3 text-xs sm:text-sm ${
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-7 h-7 rounded-lg bg-brand-600/20 text-brand-400 border border-brand-500/30 flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="w-4 h-4" />
                  </div>
                )}
                <div
                  className={`p-3.5 rounded-2xl max-w-[85%] leading-relaxed space-y-2.5 ${
                    msg.role === 'user'
                      ? 'bg-brand-600 text-white font-medium rounded-br-none shadow-md shadow-brand-500/10'
                      : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.text}</p>

                  {/* Timestamp Sources Citations */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="pt-2 border-t border-slate-800/80 mt-2">
                      <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                        Timestamp Sources:
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.sources.map((src, sIdx) => (
                          <button
                            key={sIdx}
                            onClick={() => onTimestampClick && onTimestampClick(src.start_time)}
                            className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-md bg-slate-800/90 hover:bg-brand-600/30 text-brand-300 border border-slate-700/60 transition-colors"
                            title={src.text_snippet || `Jump to ${formatSecondsToTimestamp(src.start_time)}`}
                          >
                            <PlayCircle className="w-3 h-3 text-brand-400" />
                            <span>{formatSecondsToTimestamp(src.start_time)}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                {msg.role === 'user' && (
                  <div className="w-7 h-7 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                    <UserIcon className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}

            {askMutation.isPending && (
              <div className="flex gap-3 text-xs sm:text-sm items-center text-slate-400 p-2">
                <Loader2 className="w-4 h-4 animate-spin text-brand-400" />
                <span>ExplainMe is retrieving video context and formulating answer...</span>
              </div>
            )}
          </div>

          {/* Quick sample prompt pills */}
          <div className="pt-2 flex flex-wrap gap-1.5">
            {sampleQuestions.map((sq, i) => (
              <button
                key={i}
                onClick={() => setQuestion(sq)}
                className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-brand-300 hover:border-slate-700 transition-colors"
              >
                {sq}
              </button>
            ))}
          </div>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="relative flex items-center pt-2">
            <input
              type="text"
              placeholder="Ask a question about this video..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={askMutation.isPending}
              className="w-full bg-slate-900/90 border border-slate-800 text-slate-100 rounded-xl pl-4 pr-12 py-3 text-xs sm:text-sm focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500/30"
            />
            <button
              type="submit"
              disabled={!question.trim() || askMutation.isPending}
              className="absolute right-2 p-2 rounded-lg bg-brand-600 hover:bg-brand-500 disabled:opacity-40 disabled:hover:bg-brand-600 text-white transition-colors"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </>
      )}
    </Card>
  );
};
