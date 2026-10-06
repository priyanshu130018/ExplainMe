import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Zap, Brain, MessageSquare, Clock, ArrowRight } from 'lucide-react';
import { AnalyzeForm } from '../components/dashboard/AnalyzeForm';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';

export const LandingPage: React.FC = () => {
  const features = [
    {
      icon: <Zap className="w-6 h-6 text-amber-400" />,
      bg: 'bg-amber-500/10 border-amber-500/20',
      title: 'Lightning Fast Captions Path',
      description:
        'Extracts native transcripts in seconds without downloading multi-gigabyte video or audio files.',
    },
    {
      icon: <Brain className="w-6 h-6 text-brand-400" />,
      bg: 'bg-brand-500/10 border-brand-500/20',
      title: 'Educational Deep Dives',
      description:
        'Converts 2-hour lectures or podcasts into quick overviews, comprehensive chapter breakdowns, and actionable takeaways.',
    },
    {
      icon: <MessageSquare className="w-6 h-6 text-emerald-400" />,
      bg: 'bg-emerald-500/10 border-emerald-500/20',
      title: 'Ask ExplainMe Grounded Q&A',
      description:
        'Chat with an AI tutor that answers strictly based on the spoken video transcript, eliminating hallucinations.',
    },
    {
      icon: <Clock className="w-6 h-6 text-sky-400" />,
      bg: 'bg-sky-500/10 border-sky-500/20',
      title: 'Precision Timestamp Jump',
      description:
        'Every key takeaway and transcript chunk is paired with exact video timestamps so you can jump straight to the source.',
    },
  ];

  return (
    <div className="space-y-20 py-8">
      {/* Hero Section */}
      <section className="text-center max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs font-semibold tracking-wide uppercase">
          <Sparkles className="w-3.5 h-3.5" />
          <span>The AI Video Tutor</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-black text-white tracking-tight leading-tight">
          Understand any long video in <span className="bg-gradient-to-r from-brand-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">minutes</span>, not hours.
        </h1>

        <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto font-normal leading-relaxed">
          Transform lectures, interviews, and deep tutorials into clear summaries, structured chapter insights, and interactive grounded Q&A.
        </p>

        {/* Big URL input box */}
        <div className="pt-6 max-w-3xl mx-auto">
          <AnalyzeForm />
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Designed for genuine learning & comprehension
          </h2>
          <p className="text-slate-400 text-sm max-w-lg mx-auto">
            Not just a shortener — a structured comprehension engine built to help you master video content.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feat, i) => (
            <Card key={i} hoverEffect className="space-y-3.5 p-6 border-slate-800">
              <div className={`w-12 h-12 rounded-2xl ${feat.bg} border flex items-center justify-center`}>
                {feat.icon}
              </div>
              <h3 className="text-base font-bold text-white">{feat.title}</h3>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                {feat.description}
              </p>
            </Card>
          ))}
        </div>
      </section>

      {/* Call to Action Banner */}
      <section className="glass-panel rounded-3xl p-8 sm:p-12 border border-brand-500/30 text-center relative overflow-hidden bg-gradient-to-r from-brand-950/60 via-slate-900/90 to-indigo-950/60">
        <div className="max-w-2xl mx-auto space-y-4 relative z-10">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
            Ready to supercharge your video learning?
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            Jump into the dashboard or explore past analyzed videos to see ExplainMe in action.
          </p>
          <div className="pt-2 flex justify-center gap-4">
            <Link to="/dashboard">
              <Button size="lg" rightIcon={<ArrowRight className="w-4 h-4" />}>
                Go to Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
