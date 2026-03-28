/**
 * Editorial Review API — 编辑审阅页联调契约
 *
 * 端点映射:
 *   - 稿件读取:       GET  /v1/tasks/{task_id} (复用)
 *   - 提交审阅决定:   POST /v1/editorial/submit
 *   - 审阅历史:       GET  /v1/editorial/history/{task_id}
 */

import { apiClient } from './client';

// ==================== 类型定义 ====================

export type ReviewDecision = 'approved' | 'conditional' | 'rejected';
export type AnnotationType = 'suggest' | 'must_fix' | 'question';

export interface ReviewAnnotation {
  paragraph_id: string;
  selected_text: string;
  type: AnnotationType;
  comment: string;
}

export interface PatchInstruction {
  paragraph_id: string;
  instruction: string;
}

export interface EditorialSubmitRequest {
  task_id: string;
  decision: ReviewDecision;
  overall_comment: string;
  annotations: ReviewAnnotation[];
  patches: PatchInstruction[];
}

export interface EditorialSubmitResponse {
  review_id: string;
  task_id: string;
  decision: ReviewDecision;
  status: 'submitted' | 'failed';
  error?: string;
}

export interface EditorialHistoryItem {
  review_id: string;
  decision: ReviewDecision;
  overall_comment: string;
  annotation_count: number;
  patch_count: number;
  created_at: string;
  reviewer?: string;
}

export interface EditorialHistoryResponse {
  task_id: string;
  reviews: EditorialHistoryItem[];
}

// ==================== API 函数 ====================

/**
 * 提交审阅决定
 */
export async function submitEditorialReview(request: EditorialSubmitRequest): Promise<EditorialSubmitResponse> {
  return apiClient<EditorialSubmitResponse>('/v1/editorial/submit', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * 获取审阅历史
 */
export async function getEditorialHistory(taskId: string): Promise<EditorialHistoryResponse> {
  return apiClient<EditorialHistoryResponse>(`/v1/editorial/history/${encodeURIComponent(taskId)}`);
}
