/**
 * Run Result Types
 * 
 * 执行结果展示模型
 */

import type { TargetId } from './target';
import type {
  OpinionGenerateResponse,
  SemanticReviewResponse,
  ArticleWorkflowResponse,
} from './api';

// ============ Run Status ============

export type RunStatus = 'idle' | 'running' | 'success' | 'error';

// ============ Run Result View ============

export interface RunResultView {
  runId: string;
  targetId: TargetId;
  status: RunStatus;
  summaryTitle: string;
  summaryItems: Array<{ label: string; value: string }>;
  detailSections: Array<{
    title: string;
    content: unknown;
  }>;
  childTasks?: Array<{
    moduleName: string;
    taskId: string;
    status: string;
  }>;
  errorMessage?: string;
  rawResponse?: OpinionGenerateResponse | SemanticReviewResponse | ArticleWorkflowResponse;
  launchedAt: string;
}

// ============ Task Summary ============

export interface TaskSummary {
  taskId: string;
  targetId: TargetId;
  displayName: string;
  status: RunStatus;
  launchedAt: string;
  childTaskCount: number;
  shortOutcome: string;
  source: 'page_session_cache'; // 一期固定值
}

// ============ Result Transformer Functions ============

export function transformOpinionResponse(
  response: OpinionGenerateResponse,
  launchedAt: string
): RunResultView {
  return {
    runId: response.task_id,
    targetId: 'opinion',
    status: 'success',
    summaryTitle: '观点生成完成',
    summaryItems: [
      { label: '核心观点', value: response.thesis.statement.slice(0, 100) + '...' },
      { label: '置信度', value: `${(response.thesis.confidence * 100).toFixed(0)}%` },
      { label: '支撑点数量', value: `${response.support_points.length}` },
    ],
    detailSections: [
      { title: '核心观点', content: response.thesis },
      { title: '支撑点', content: response.support_points },
      { title: '置信度说明', content: response.confidence_notes },
    ],
    launchedAt,
    rawResponse: response,
  };
}

export function transformSemanticReviewResponse(
  response: SemanticReviewResponse,
  launchedAt: string
): RunResultView {
  const passedText = response.passed ? '通过' : '未通过';
  return {
    runId: response.task_id,
    targetId: 'semantic_review',
    status: 'success',
    summaryTitle: `语义审核${passedText}`,
    summaryItems: [
      { label: '审核结果', value: passedText },
      { label: '原型对齐分数', value: response.prototype_alignment ? `${response.prototype_alignment.score}分` : 'N/A' },
      { label: '问题数量', value: `${response.findings.length}` },
    ],
    detailSections: [
      { title: '严重性统计', content: response.severity_summary },
      { title: '发现问题', content: response.findings },
      { title: '改写建议', content: response.rewrite_target },
      { title: '原型对齐', content: response.prototype_alignment },
    ],
    launchedAt,
    rawResponse: response,
  };
}

export function transformArticleWorkflowResponse(
  response: ArticleWorkflowResponse,
  launchedAt: string
): RunResultView {
  const hasErrors = response.errors.length > 0;
  return {
    runId: response.task_id,
    targetId: 'article',
    status: hasErrors ? 'error' : 'success',
    summaryTitle: hasErrors ? '工作流执行失败' : '工作流执行完成',
    summaryItems: [
      { label: '执行状态', value: response.status },
      { label: '子任务数量', value: `${response.child_task_ids.length}` },
      { label: '原型对齐分数', value: response.prototype_alignment ? `${response.prototype_alignment.score}分` : 'N/A' },
    ],
    detailSections: [
      { title: '子任务结果', content: response.child_results },
      { title: '原型对齐', content: response.prototype_alignment },
      { title: '错误信息', content: response.errors },
    ],
    childTasks: response.child_results.map(cr => ({
      moduleName: cr.module_name,
      taskId: cr.task_id,
      status: cr.status,
    })),
    errorMessage: hasErrors ? response.errors.join('; ') : undefined,
    launchedAt,
    rawResponse: response,
  };
}

// ============ Task Summary Transformer ============

export function createTaskSummary(
  result: RunResultView,
  displayName: string
): TaskSummary {
  return {
    taskId: result.runId,
    targetId: result.targetId,
    displayName,
    status: result.status,
    launchedAt: result.launchedAt,
    childTaskCount: result.childTasks?.length ?? 0,
    shortOutcome: result.summaryTitle,
    source: 'page_session_cache',
  };
}