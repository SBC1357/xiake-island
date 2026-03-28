/**
 * Run Status Banner
 * 
 * 执行状态横幅
 */

import { Badge } from './ui';
import type { RunStatus } from '../types';

export interface RunStatusBannerProps {
  status: RunStatus;
  message?: string;
}

export function RunStatusBanner({ status, message }: RunStatusBannerProps) {
  const statusConfig: Record<RunStatus, { variant: 'default' | 'success' | 'warning' | 'danger' | 'info'; label: string }> = {
    idle: { variant: 'default', label: '等待执行' },
    running: { variant: 'info', label: '执行中...' },
    success: { variant: 'success', label: '执行成功' },
    error: { variant: 'danger', label: '执行失败' },
  };
  
  const config = statusConfig[status];
  
  return (
    <div className="flex items-center gap-2">
      <Badge variant={config.variant}>{config.label}</Badge>
      {message && <span className="text-sm text-gray-600">{message}</span>}
    </div>
  );
}