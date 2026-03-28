/**
 * Badge Component
 */

import { forwardRef, type HTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md';
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'default', size = 'md', children, ...props }, ref) => {
    const variantClassName = {
      default: 'badge-neutral',
      success: 'badge-success',
      warning: 'badge-warning',
      danger: 'badge-danger',
      info: 'badge-brand',
    }[variant];
    
    return (
      <span
        ref={ref}
        className={cn(
          variantClassName,
          size === 'sm' && 'px-2 py-0.5 text-[0.65rem]',
          size === 'md' && 'px-2.5 py-0.5 text-xs',
          className
        )}
        {...props}
      >
        {children}
      </span>
    );
  }
);
Badge.displayName = 'Badge';