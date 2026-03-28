/**
 * HistoryPanel
 *
 * 任务历史面板组件，显示历史任务列表，支持加载参数
 */

import { useState, useCallback } from 'react';
import { Card, CardHeader, CardBody, Badge, Button, Spinner } from './ui';
import { useTaskHistory } from '../hooks/useTaskHistory';
import { copyTask } from '../api/tasks';
import type { TaskDetail, TaskListItem } from '../api/tasks';
import type {
  OpinionDraftConfig,
  SemanticReviewDraftConfig,
} from '../types/draft';

export interface HistoryPanelProps {
  /** 选择任务后填充表单的回调 */
  onLoadParams: (module: string, params: Record<string, unknown>, sourceTaskId?: string) => void;
  /** 复制任务后的回调 */
  onCopy?: (newTaskId: string, originalTaskId: string) => void;
  /** 可选的高度限制 */
  maxHeight?: string;
}

const MODULE_LABELS: Record<string, string> = {
  opinion: '观点生成',
  semantic_review: '语义审核',
  orchestrator: '工作流',
};

const STATUS_VARIANTS: Record<string, 'success' | 'danger' | 'warning' | 'default'> = {
  completed: 'success',
  failed: 'danger',
  running: 'warning',
};

const STATUS_LABELS: Record<string, string> = {
  completed: '完成',
  failed: '失败',
  running: '运行中',
};

export function HistoryPanel({ onLoadParams, onCopy, maxHeight = '400px' }: HistoryPanelProps) {
  const { tasks, total, loading, error, refresh, getDetail } = useTaskHistory({
    defaultParams: { limit: 20 },
  });

  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<TaskDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [copying, setCopying] = useState(false);
  const [copyResult, setCopyResult] = useState<{ newTaskId: string } | null>(null);

  // 点击任务项
  const handleTaskClick = useCallback(async (task: TaskListItem) => {
    setSelectedTaskId(task.task_id);
    setLoadingDetail(true);
    setCopyResult(null);
    const detail = await getDetail(task.task_id);
    setSelectedDetail(detail);
    setLoadingDetail(false);
  }, [getDetail]);

  // 加载参数到表单
  const handleLoadParams = useCallback(() => {
    if (!selectedDetail || !selectedDetail.input_data) return;

    const module = selectedDetail.module;
    const input = selectedDetail.input_data;
    const taskId = selectedDetail.task_id;

    // 根据模块转换参数格式
    if (module === 'opinion') {
      const params: OpinionDraftConfig = {
        audience: (input.audience as string) || '',
        evidenceItems: extractEvidenceItems(input.evidence_bundle),
        evidenceSummary: (input.evidence_bundle as Record<string, unknown>)?.summary as string || '',
        thesisHint: (input.thesis_hint as string) || '',
        contextMetadataText: formatContextMetadata(input.context_metadata),
      };
      onLoadParams(module, params as unknown as Record<string, unknown>, taskId);
    } else if (module === 'semantic_review') {
      const params: SemanticReviewDraftConfig = {
        content: (input.content as string) || '',
        audience: (input.audience as string) || '',
        prototypeHint: (input.prototype_hint as string) || '',
        register: (input.register as string) || '',
        contextMetadataText: formatContextMetadata(input.context_metadata),
      };
      onLoadParams(module, params as unknown as Record<string, unknown>, taskId);
    } else if (module === 'orchestrator') {
      // 工作流参数较复杂，简化处理
      onLoadParams(module, input, taskId);
    }

    // 清除选中状态
    setSelectedTaskId(null);
    setSelectedDetail(null);
  }, [selectedDetail, onLoadParams]);

  // 复制任务参数创建新任务记录
  const handleCopy = useCallback(async () => {
    if (!selectedDetail) return;
    
    const confirmed = window.confirm('确定要复制此任务的输入参数吗？将创建新任务记录（不执行），原任务不会被删除。');
    if (!confirmed) return;
    
    setCopying(true);
    try {
      const result = await copyTask(selectedDetail.task_id);
      setCopyResult({ newTaskId: result.new_task_id });
      
      // 回调通知
      if (onCopy) {
        onCopy(result.new_task_id, result.original_task_id);
      }
      
      // 刷新列表
      refresh();
    } catch (e) {
      console.error('Copy failed:', e);
      alert('复制任务失败');
    } finally {
      setCopying(false);
    }
  }, [selectedDetail, onCopy, refresh]);

  // 格式化时间
  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-900">任务历史</h3>
        <Button variant="ghost" size="sm" onClick={refresh} disabled={loading}>
          {loading ? <Spinner size="sm" /> : '刷新'}
        </Button>
      </CardHeader>
      <CardBody style={{ maxHeight }} className="overflow-y-auto">
        {error && (
          <p className="text-sm text-red-600 text-center py-4">{error}</p>
        )}

        {tasks.length === 0 && !loading && !error && (
          <p className="text-sm text-gray-500 text-center py-4">暂无历史任务</p>
        )}

        <div className="space-y-2">
          {tasks.map((task) => (
            <button
              key={task.task_id}
              type="button"
              className={`w-full text-left p-3 rounded-md border cursor-pointer transition-colors ${
                selectedTaskId === task.task_id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:bg-gray-50'
              }`}
              onClick={() => handleTaskClick(task)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant={STATUS_VARIANTS[task.status] || 'default'} size="sm">
                    {STATUS_LABELS[task.status] || task.status}
                  </Badge>
                  <span className="text-sm font-medium text-gray-800">
                    {MODULE_LABELS[task.module] || task.module}
                  </span>
                </div>
                <span className="text-xs text-gray-400">
                  {formatTime(task.started_at)}
                </span>
              </div>
              {task.error_message && (
                <p className="mt-1 text-xs text-red-600 truncate">{task.error_message}</p>
              )}
            </button>
          ))}
        </div>

        {/* 选中任务的详情和操作 */}
        {selectedTaskId && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">已选任务</span>
              {loadingDetail && <Spinner size="sm" />}
            </div>

            {selectedDetail && (
              <div className="space-y-2">
                <p className="text-xs text-gray-500">
                  任务ID: {selectedDetail.task_id.slice(0, 8)}...
                </p>
                <p className="text-xs text-gray-500">
                  输入哈希: {selectedDetail.input_hash || '无'}
                </p>

                {selectedDetail.input_data && (
                  <>
                    <Button
                      variant="primary"
                      size="sm"
                      className="w-full"
                      onClick={handleLoadParams}
                    >
                      加载参数到表单
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full"
                      onClick={handleCopy}
                      disabled={copying}
                    >
                      {copying ? '复制中...' : '复制任务'}
                    </Button>
                  </>
                )}

                {!selectedDetail.input_data && (
                  <p className="text-xs text-gray-400 text-center">无可用参数</p>
                )}

                {copyResult && (
                  <p className="text-xs text-green-600 text-center">
                    已创建任务记录: {copyResult.newTaskId.slice(0, 8)}...（未执行）
                  </p>
                )}
              </div>
            )}
          </div>
        )}

        {total > tasks.length && (
          <p className="mt-3 text-xs text-gray-400 text-center">
            显示 {tasks.length} / {total} 条
          </p>
        )}
      </CardBody>
    </Card>
  );
}

// 辅助函数：提取证据项
function extractEvidenceItems(
  evidenceBundle: unknown
): Array<{ id: string; content: string; source?: string; relevance?: number }> {
  if (!evidenceBundle || typeof evidenceBundle !== 'object') return [];

  const bundle = evidenceBundle as Record<string, unknown>;
  const items = bundle.items;

  if (!Array.isArray(items)) return [];

  return items.map((item: Record<string, unknown>) => ({
    id: (item.id as string) || '',
    content: (item.content as string) || '',
    source: item.source as string | undefined,
    relevance: item.relevance as number | undefined,
  }));
}

// 辅助函数：格式化上下文元数据
function formatContextMetadata(metadata: unknown): string {
  if (!metadata) return '';
  if (typeof metadata === 'object') {
    return JSON.stringify(metadata, null, 2);
  }
  return String(metadata);
}