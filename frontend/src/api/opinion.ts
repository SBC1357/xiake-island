/**
 * Opinion API
 */

import { apiClient, ApiError } from './client';
import type { OpinionGenerateRequest, OpinionGenerateResponse } from '../types';

export async function generateOpinion(
  request: OpinionGenerateRequest
): Promise<OpinionGenerateResponse> {
  return apiClient<OpinionGenerateResponse>('/v1/opinion/generate', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export { ApiError };