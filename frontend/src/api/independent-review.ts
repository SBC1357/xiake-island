/**
 * Independent Review API Client
 *
 * 独立改稿审稿模块 API。
 */

import { apiClient, API_BASE_URL, ApiError } from './client';

// ============ Types ============

export interface TextReviewRequest {
  content: string;
  audience?: string;
  rule_mode?: 'default' | 'custom';
  custom_rules?: string[];
  prototype_hint?: string;
  register?: string;
}

export interface ReviewFinding {
  severity: string;
  category: string;
  description: string;
  location?: string;
  suggestion?: string;
}

export interface ReviewRewriteTarget {
  original: string;
  suggested: string;
  reason: string;
  priority: string;
}

export interface IndependentReviewResponse {
  review_id: string;
  input_mode: string;
  rule_mode: string;
  passed: boolean;
  severity_summary: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  findings: ReviewFinding[];
  rewrite_targets: ReviewRewriteTarget[];
  rule_layer_output?: Record<string, unknown>;
  model_review_output?: Record<string, unknown>;
  original_content?: string;
  debug_info?: Record<string, unknown>;
}

// ============ API Functions ============

/**
 * 文本审改
 */
export async function reviewText(
  request: TextReviewRequest
): Promise<IndependentReviewResponse> {
  return apiClient<IndependentReviewResponse>('/v1/review/independent/text', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * DOCX 审改
 */
export async function reviewDocx(
  file: File,
  options: {
    audience?: string;
    rule_mode?: 'default' | 'custom';
    custom_rules?: string;
    prototype_hint?: string;
    register?: string;
  } = {}
): Promise<IndependentReviewResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (options.audience) formData.append('audience', options.audience);
  if (options.rule_mode) formData.append('rule_mode', options.rule_mode);
  if (options.custom_rules) formData.append('custom_rules', options.custom_rules);
  if (options.prototype_hint) formData.append('prototype_hint', options.prototype_hint);
  if (options.register) formData.append('register', options.register);

  const response = await fetch(`${API_BASE_URL}/v1/review/independent/docx`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({ detail: 'Review failed' }));
    throw new ApiError(response.status, data.detail || 'Review failed');
  }

  return response.json();
}

export { ApiError };
