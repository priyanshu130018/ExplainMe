import React from 'react';
import { cn } from '../../lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'info' | 'purple' | 'danger';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  className,
  variant = 'default',
  size = 'md',
  children,
  ...props
}) => {
  const variants = {
    default: 'bg-slate-800/80 text-slate-300 border-slate-700/60',
    success: 'bg-emerald-950/70 text-emerald-300 border-emerald-800/50',
    warning: 'bg-amber-950/70 text-amber-300 border-amber-800/50',
    info: 'bg-sky-950/70 text-sky-300 border-sky-800/50',
    purple: 'bg-brand-950/70 text-brand-300 border-brand-800/50',
    danger: 'bg-red-950/70 text-red-300 border-red-800/50',
  };

  const sizes = {
    sm: 'text-[11px] px-2 py-0.5 font-medium rounded-md',
    md: 'text-xs px-2.5 py-1 font-semibold rounded-lg',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 border tracking-wide uppercase',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};
