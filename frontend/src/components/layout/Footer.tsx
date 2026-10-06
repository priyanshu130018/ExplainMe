import React from 'react';
import { Sparkles, Heart } from 'lucide-react';
import { APP_NAME } from '../../lib/constants';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-slate-800/80 bg-slate-950/60 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-slate-400 text-xs">
          <Sparkles className="w-4 h-4 text-brand-400" />
          <span>&copy; {new Date().getFullYear()} {APP_NAME}. AI Video Understanding & Tutoring.</span>
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-500">
          <span>Powered by Mistral & Celery</span>
          <span>•</span>
          <span className="flex items-center gap-1">
            Built with <Heart className="w-3 h-3 text-red-500 fill-red-500/30" /> for learning
          </span>
        </div>
      </div>
    </footer>
  );
};
