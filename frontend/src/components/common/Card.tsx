import React from 'react';
import { cn } from '../../lib/utils';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverEffect?: boolean;
}

export const Card: React.FC<CardProps> = ({
  className,
  hoverEffect = false,
  children,
  ...props
}) => {
  return (
    <div
      className={cn(
        'glass-panel rounded-2xl p-6 transition-all duration-300',
        hoverEffect && 'hover:border-slate-700/80 hover:bg-slate-900/90 hover:shadow-xl hover:shadow-brand-500/5',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
