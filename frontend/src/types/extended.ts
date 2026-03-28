/**
 * Extended API Type Definitions for SP-3
 * 
 * 匹配后端 Pydantic 模型
 */

// ============ Evidence Types ============

export interface EvidenceQueryRequest {
  product_id: string;
  domain?: string;
  fact_keys?: string[];
  limit?: number;
}

export interface FactRecord {
  fact_id: string;
  product_id: string;
  domain: string;
  fact_key: string;
  value: string;
  definition?: string;
  definition_zh?: string;
  unit?: string;
  status: string;
  lineage: Record<string, unknown>;
}

export interface SourceRecord {
  source_id: string;
  source_type: string;
  title: string;
  product_id?: string;
  source_keys: string[];
}

export interface FactLineage {
  fact_id: string;
  product_id?: string;
  lineage: Record<string, unknown>;
  sources: string[];
}

export interface ProductListResponse {
  products: string[];
  count: number;
}

// ============ Planning Types ============

export interface RouteContextRequest {
  product_id: string;
  register?: string;
  audience: string;
  project_name?: string;
  deliverable_type?: string;
  metadata?: Record<string, unknown>;
}

export interface PlanningRequest {
  context: RouteContextRequest;
  evidence_facts?: Record<string, unknown>[];
  selected_facts?: string[];
}

export interface OutlineItem {
  title: string;
  type: string;
  domain?: string;
  fact_count?: number;
  fact_id?: string;
}

export interface PlanningResponse {
  task_id: string;
  thesis?: string;
  outline: OutlineItem[];
  play_id?: string;
  arc_id?: string;
  target_audience?: string;
  key_evidence?: string[];
  style_notes?: Record<string, unknown>;
}

// ============ Writing Types ============

export interface WritingRequest {
  thesis: string;
  outline: Record<string, unknown>[];
  play_id?: string;
  arc_id?: string;
  target_audience?: string;
  key_evidence?: string[];
  style_notes?: Record<string, unknown>;
}

export interface CompiledPromptResponse {
  task_id: string;
  system_prompt: string;
  user_prompt: string;
  llm_config: Record<string, unknown>;
  extra_info: Record<string, unknown>;
}

// ============ Drafting Types (SP-7D) ============

/**
 * 成稿请求 - 匹配后端 DraftingRequest
 * Backend Contract: POST /v1/drafting/generate
 */
export interface DraftingRequest {
  /** 系统级指令 (required) */
  system_prompt: string;
  /** 用户级指令 (required) */
  user_prompt: string;
  /** 模型配置 (optional) */
  model_config_data?: Record<string, unknown>;
  /** 目标字数 (optional) */
  target_word_count?: number;
  /** 元数据 (optional) */
  metadata?: Record<string, unknown>;
}

/**
 * 成稿追踪信息
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
 * 成稿结果 - 匹配后端 DraftingResponse
 */
export interface DraftingResult {
  /** 任务ID */
  task_id: string;
  /** 生成的正文内容 (真正的文章内容，非 prompt) */
  content: string;
  /** 正文字数 */
  word_count: number;
  /** 成稿追踪 */
  trace?: DraftingTrace;
  /** 元数据 */
  metadata?: Record<string, unknown>;
}

// ============ Quality Types ============

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

// ============ Delivery Types ============

export interface DeliveryRequest {
  thesis: string;
  outline: Record<string, unknown>[];
  key_evidence?: string[];
  content?: string;
  target_audience?: string;
  play_id?: string;
  arc_id?: string;
}

export interface DeliveryResult {
  task_id: string;
  output_path: string;
  summary: Record<string, unknown>;
  artifacts: string[];
}

export interface DeliveryHistoryItem {
  filename: string;
  path: string;
  created_at?: string;
}

export interface DeliveryHistory {
  items: DeliveryHistoryItem[];
  count: number;
}

// ============ Workflow Route Types ============

export interface WorkflowRoute {
  id: string;
  name: string;
  description: string;
  modules: string[];
  phase: '一期' | '二期' | '三期';
}

export const WORKFLOW_ROUTES: WorkflowRoute[] = [
  {
    id: 'standard',
    name: '标准六段链',
    description: 'Evidence → Planning → Writing → Drafting → Quality → Delivery',
    modules: ['evidence', 'planning', 'writing', 'drafting', 'quality', 'delivery'],
    phase: '一期',
  },
  {
    id: 'quick-opinion',
    name: '快速观点',
    description: 'Evidence → Opinion',
    modules: ['evidence', 'opinion'],
    phase: '二期',
  },
  {
    id: 'audit-rewrite',
    name: '审核重写',
    description: 'Semantic Review → Writing',
    modules: ['semantic_review', 'writing'],
    phase: '二期',
  },
];