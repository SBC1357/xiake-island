/**
 * Semantic Review API
 */

import { apiClient, ApiError } from './client';
import type { SemanticReviewRequest, SemanticReviewResponse } from '../types';

export async function reviewSemantic(
  request: SemanticReviewRequest
): Promise<SemanticReviewResponse> {
  return apiClient<SemanticReviewResponse>('/v1/review/semantic', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export { ApiError };