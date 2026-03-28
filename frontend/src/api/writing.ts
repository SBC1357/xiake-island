/**
 * Writing API Client
 */

import { apiClient, ApiError } from './client';

// ============ Types ============

export interface WritingRequest {
  thesis: string;
  outline: Record<string, unknown>[];
  play_id?: string;
  arc_id?: string;
  target_audience?: string;
  key_evidence?: string[];
  style_notes?: Record<string, unknown>;
}

export interface WritingWithEvidenceRequest {
  thesis: string;
  outline: Record<string, unknown>[];
  evidence_facts: Record<string, unknown>[];
  play_id?: string;
  arc_id?: string;
  target_audience?: string;
  style_notes?: Record<string, unknown>;
}

export interface CompiledPromptResponse {
  task_id: string;
  system_prompt: string;
  user_prompt: string;
  llm_config: Record<string, unknown>;
  extra_info: Record<string, unknown>;
}

// ============ API Functions ============

/**
 * Compile draft prompt
 */
export async function compileDraft(request: WritingRequest): Promise<CompiledPromptResponse> {
  return apiClient<CompiledPromptResponse>('/v1/writing/draft', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Compile draft with evidence
 */
export async function compileDraftWithEvidence(request: WritingWithEvidenceRequest): Promise<CompiledPromptResponse> {
  return apiClient<CompiledPromptResponse>('/v1/writing/draft-with-evidence', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export { ApiError };