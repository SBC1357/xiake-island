/**
 * Recent Run List
 * 
 * 最近执行列表（当前会话内）
 */

import { Card, CardHeader, CardBody, Badge } from './ui';
import type { TaskSummary } from '../types';

export interface RecentRunListProps {
  runs: TaskSummary[];
  onSelectRun?: (run: TaskSummary) => void;
}

export function RecentRunList({ runs, onSelectRun }: RecentRunListProps) {
  if (runs.length === 0) {
    return (
      <Card>
        <CardHeader>
          <h3 className="text-sm font-medium text-gray-900">最近执行</h3>
        </CardHeader>
        <CardBody>
          <p className="text-sm text-gray-500 text-center py-4">
            暂无执行记录
          </p>
        </CardBody>
      </Card>
    );
  }
  
  const statusColors: Record<string, 'success' | 'danger' | 'warning' | 'default'> = {
    success: 'success',
    error: 'danger',
    running: 'warning',
    idle: 'default',
  };
  
  const statusLabels: Record<string, string> = {
    success: '成功',
    error: '失败',
    running: '运行中',
    idle: '待执行',
  };
  
  return (
    <Card>
      <CardHeader>
        <h3 className="text-sm font-medium text-gray-900">最近执行</h3>
      </CardHeader>
      <CardBody className="space-y-2">
        {runs.slice(0, 5).map((run) => (
          <div
            key={run.taskId}
            className="flex items-center justify-between p-2 rounded-md hover:bg-gray-50 cursor-pointer"
            onClick={() => onSelectRun?.(run)}
          >
            <div className="flex items-center gap-2">
              <Badge variant={statusColors[run.status]} size="sm">
                {statusLabels[run.status]}
              </Badge>
              <span className="text-sm text-gray-800">{run.displayName}</span>
            </div>
            <span className="text-xs text-gray-400">
              {new Date(run.launchedAt).toLocaleTimeString()}
            </span>
          </div>
        ))}
      </CardBody>
    </Card>
  );
}