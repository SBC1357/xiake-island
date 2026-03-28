/**
 * Workflow API
 */

import { apiClient, ApiError } from './client';
import type { ArticleWorkflowRequest, ArticleWorkflowResponse } from '../types';

export async function executeArticleWorkflow(
  request: ArticleWorkflowRequest
): Promise<ArticleWorkflowResponse> {
  return apiClient<ArticleWorkflowResponse>('/v1/workflow/article', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// ============ Standard Chain Workflow ============

export interface StandardChainWorkflowRequest {
  product_id: string;
  domain?: string;
  register?: string;
  audience: string;
  project_name?: string;
  target_word_count?: number;
  metadata?: Record<string, unknown>;
}

export interface ChildTaskResult {
  module_name: string;
  task_id: string;
  status: string;
  result?: Record<string, unknown>;
  error?: string;
}

export interface StandardChainWorkflowResponse {
  task_id: string;
  child_task_ids: string[];
  status: string;
  result?: Record<string, unknown>;
  child_results: ChildTaskResult[];
  errors: string[];
}

export async function executeStandardChainWorkflow(
  request: StandardChainWorkflowRequest
): Promise<StandardChainWorkflowResponse> {
  return apiClient<StandardChainWorkflowResponse>('/v1/workflow/standard-chain', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// ============ Knowledge Assets ============

export interface KnowledgeAssetsResponse {
  consumer_assets_count: number;
  rules_assets_count: number;
  consumer_root: string | null;
  has_l2: boolean;
  l2_files: string[];
}

export async function getKnowledgeAssets(): Promise<KnowledgeAssetsResponse> {
  return apiClient<KnowledgeAssetsResponse>('/v1/workflow/knowledge-assets');
}

export { ApiError };