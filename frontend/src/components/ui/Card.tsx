/**
 * Card Component
 */

import { forwardRef, type HTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'outlined' | 'interactive';
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          variant === 'interactive' ? 'card-interactive' : 'card-base',
          variant === 'default' && 'border-slate-200/60 shadow-sm bg-white',
          variant === 'outlined' && 'border-slate-200 shadow-none bg-white',
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
Card.displayName = 'Card';

export const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, children, ...props }, ref) => {
    return (
      <div 
        ref={ref} 
        className={cn("px-5 py-4 border-b border-slate-100 flex items-center justify-between", className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);
CardHeader.displayName = 'CardHeader';

export const CardBody = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, children, ...props }, ref) => {
    return (
      <div ref={ref} className={cn("px-5 py-5", className)} {...props}>
        {children}
      </div>
    );
  }
);
CardBody.displayName = 'CardBody';

export const CardFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, children, ...props }, ref) => {
    return (
      <div ref={ref} className={cn("px-5 py-4 border-t border-slate-100 bg-slate-50/50 rounded-b-xl flex items-center justify-end", className)} {...props}>
        {children}
      </div>
    );
  }
);
CardFooter.displayName = 'CardFooter';