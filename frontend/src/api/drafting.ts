/**
 * Drafting API Client
 * 
 * SP-7D: 成稿步骤 API - 将写作指令(prompt)转换为正文内容
 * 
 * Backend Contract: POST /v1/drafting/generate
 * 
 * 术语说明:
 * - Writing (写作指令): 生成 system_prompt 和 user_prompt
 * - Drafting (成稿): 将 prompts 转换为实际文章内容
 */

import { apiClient, ApiError } from './client';

// ============ Types ============

/**
 * 成稿请求 - 匹配后端 DraftingRequest (Pydantic, extra="forbid")
 */
export interface DraftingRequest {
  /** 系统级指令 (必填) */
  system_prompt: string;
  /** 用户级指令 (必填) */
  user_prompt: string;
  /** 模型配置 (可选) */
  model_config_data?: Record<string, unknown>;
  /** 目标字数 (可选) */
  target_word_count?: number;
  /** 元数据 (可选) */
  metadata?: Record<string, unknown>;
}

/**
 * 成稿追踪 - 匹配后端 DraftingTrace.to_dict()
 */
export interface DraftingTrace {
  prompt_tokens?: number;
  completion_tokens?: number;
  model_used?: string;
  latency_ms?: number;
  generation_mode?: 'fake' | 'openai';
  deterministic_seed?: string;
}

/**
 * 成稿结果 - 匹配后端 DraftingResponse (Pydantic, extra="forbid")
 */
export interface DraftingResult {
  /** 任务 ID */
  task_id: string;
  /** 生成的正文内容 */
  content: string;
  /** 正文字数 */
  word_count: number;
  /** 成稿追踪 */
  trace?: DraftingTrace;
  /** 元数据 */
  metadata?: Record<string, unknown>;
}

// ============ API Functions ============

/**
 * 执行成稿 - 将写作指令转化为正文内容
 * 
 * Endpoint: POST /v1/drafting/generate
 */
export async function executeDrafting(request: DraftingRequest): Promise<DraftingResult> {
  return apiClient<DraftingResult>('/v1/drafting/generate', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export { ApiError };