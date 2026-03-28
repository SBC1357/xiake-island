/**
 * Rewrite API — 改稿工作区联调契约
 *
 * 端点映射:
 *   - 稿件/brief 读取: GET /v1/tasks/{task_id} (复用)
 *   - 执行改稿:       POST /v1/rewrite/execute
 *   - 改稿历史:       GET  /v1/rewrite/history/{task_id}
 */

import { apiClient } from './client';

// ==================== 类型定义 ====================

export type RewriteMode = 'expand_patch' | 'dedupe_patch' | 'deepen_patch' | 'mixed_patch';

export type ParagraphAction = 'default' | 'lock' | 'expand' | 'compress' | 'deepen';

export interface ParagraphInstruction {
  paragraph_id: string;
  action: ParagraphAction;
}

export interface FrozenBrief {
  locked_sections: string[];
  must_keep_points: string[];
  must_delete_points: string[];
  forbidden_topics: string[];
  word_count_target: { min: number; max: number };
  evidence_gaps: Array<{ position: string; missing: string }>;
}

export interface RewriteExecuteRequest {
  task_id: string;
  mode: RewriteMode;
  paragraph_instructions: ParagraphInstruction[];
  brief: FrozenBrief;
}

export interface RewriteParagraphResult {
  paragraph_id: string;
  old_text: string;
  new_text: string;
  status: 'unchanged' | 'modified' | 'added' | 'removed';
}

export interface RewriteExecuteResponse {
  task_id: string;
  rewrite_task_id: string;
  status: 'completed' | 'failed' | 'running';
  mode: RewriteMode;
  paragraphs: RewriteParagraphResult[];
  word_delta: number;
  error?: string;
}

export interface RewriteHistoryItem {
  rewrite_task_id: string;
  mode: RewriteMode;
  version_label: string;
  created_at: string;
  word_count: number;
  word_delta: number;
  status: string;
}

export interface RewriteHistoryResponse {
  task_id: string;
  history: RewriteHistoryItem[];
}

// ==================== API 函数 ====================

/**
 * 执行改稿
 */
export async function executeRewrite(request: RewriteExecuteRequest): Promise<RewriteExecuteResponse> {
  return apiClient<RewriteExecuteResponse>('/v1/rewrite/execute', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * 获取改稿历史
 */
export async function getRewriteHistory(taskId: string): Promise<RewriteHistoryResponse> {
  return apiClient<RewriteHistoryResponse>(`/v1/rewrite/history/${encodeURIComponent(taskId)}`);
}
