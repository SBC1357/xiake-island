/**
 * Quality API Client
 */

import { apiClient, ApiError } from './client';

// ============ Types ============

export interface QualityReviewRequest {
  content: string;
  enabled_gates?: string[];
}

export interface QualityResult {
  task_id: string;
  overall_status: string;
  gates_passed: string[];
  warnings: Array<{ gate: string; message: string }>;
  errors: Array<{ gate: string; message: string }>;
}

export interface SemanticCheckResult {
  issues: string[];
  suggestions: string[];
  passed: boolean;
}

// ============ API Functions ============

/**
 * Review content quality
 */
export async function reviewQuality(request: QualityReviewRequest): Promise<QualityResult> {
  return apiClient<QualityResult>('/v1/quality/review', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Semantic check
 */
export async function semanticCheck(content: string): Promise<SemanticCheckResult> {
  return apiClient<SemanticCheckResult>('/v1/quality/semantic-check', {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

export { ApiError };