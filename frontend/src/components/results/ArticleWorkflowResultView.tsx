/**
 * Article Workflow Result View
 * 
 * 文章工作流结果视图
 */

import { Card, CardHeader, CardBody, Badge } from '../ui';
import { ResultActions } from '../ui/ResultActions';
import type { ArticleWorkflowResponse } from '../../types';

export interface ArticleWorkflowResultViewProps {
  result: ArticleWorkflowResponse;
}

const statusColors: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
  completed: 'success',
  running: 'warning',
  failed: 'danger',
  pending: 'default',
};

const statusLabels: Record<string, string> = {
  completed: '已完成',
  running: '运行中',
  failed: '失败',
  pending: '待执行',
};

export function ArticleWorkflowResultView({ result }: ArticleWorkflowResultViewProps) {
  const hasErrors = result.errors.length > 0;
  
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900">工作流状态</h3>
            <Badge variant={statusColors[result.status] || 'default'}>
              {statusLabels[result.status] || result.status}
            </Badge>
          </div>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-500">父任务ID</p>
              <p className="text-sm font-mono text-gray-800">{result.task_id}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">子任务数量</p>
              <p className="text-sm font-medium text-gray-800">{result.child_task_ids.length}</p>
            </div>
          </div>
        </CardBody>
      </Card>
      
      {result.child_results.length > 0 && (
        <Card>
          <CardHeader>
            <h3 className="text-sm font-medium text-gray-900">子任务结果</h3>
          </CardHeader>
          <CardBody className="space-y-3">
            {result.child_results.map((child) => (
              <div key={child.task_id} className="border border-gray-200 rounded-md p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Badge variant={child.module_name === 'opinion' ? 'success' : 'warning'} size="sm">
                      {child.module_name}
                    </Badge>
                    <Badge variant={statusColors[child.status] || 'default'} size="sm">
                      {statusLabels[child.status] || child.status}
                    </Badge>
                  </div>
                  <span className="text-xs text-gray-400 font-mono">{child.task_id}</span>
                </div>
                {child.error && (
                  <p className="text-sm text-red-600">{child.error}</p>
                )}
                {child.result && (
                  <p className="text-xs text-gray-500">结果已生成</p>
                )}
              </div>
            ))}
          </CardBody>
        </Card>
      )}
      
      {result.prototype_alignment && (
        <Card>
          <CardHeader>
            <h3 className="text-sm font-medium text-gray-900">原型对齐</h3>
          </CardHeader>
          <CardBody>
            <div className="flex items-center gap-4 mb-3">
              <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className={`h-full ${result.prototype_alignment.score >= 80 ? 'bg-green-500' : result.prototype_alignment.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                  style={{ width: `${result.prototype_alignment.score}%` }}
                />
              </div>
              <span className="text-sm font-medium">{result.prototype_alignment.score}分</span>
            </div>
            {result.prototype_alignment.notes && (
              <p className="text-sm text-gray-600">{result.prototype_alignment.notes}</p>
            )}
          </CardBody>
        </Card>
      )}
      
      {hasErrors && (
        <Card>
          <CardHeader>
            <h3 className="text-sm font-medium text-red-600">错误信息</h3>
          </CardHeader>
          <CardBody>
            <ul className="list-disc list-inside text-sm text-red-600 space-y-1">
              {result.errors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </CardBody>
        </Card>
      )}
      
      <ResultActions
        data={result as unknown as Record<string, unknown>}
        taskId={result.task_id}
        moduleName="orchestrator"
      />
    </div>
  );
}