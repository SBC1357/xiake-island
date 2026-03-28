/**
 * API Type Definitions
 * 
 * 匹配后端 Pydantic 模型 (extra="forbid")
 */

// ============ Opinion Types ============

export interface EvidenceItem {
  id: string;
  content: string;
  source?: string;
  relevance?: number;
}

export interface EvidenceBundle {
  items: EvidenceItem[];
  summary?: string;
}

export interface OpinionGenerateRequest {
  evidence_bundle: EvidenceBundle;
  audience: string;
  thesis_hint?: string;
  context_metadata?: Record<string, unknown>;
}

export interface Thesis {
  statement: string;
  confidence: number;
  evidence_refs: string[];
}

export interface SupportPoint {
  content: string;
  strength: string;
  evidence_id?: string;
}

export interface ConfidenceNotes {
  overall_confidence: number;
  limitations: string[];
  assumptions: string[];
}

export interface OpinionGenerateResponse {
  task_id: string;
  thesis: Thesis;
  support_points: SupportPoint[];
  confidence_notes?: ConfidenceNotes;
}

// ============ Semantic Review Types ============

export interface SemanticReviewRequest {
  content: string;
  audience: string;
  prototype_hint?: string;
  register?: string;
  context_metadata?: Record<string, unknown>;
}

export interface SeveritySummary {
  low: number;
  medium: number;
  high: number;
  critical: number;
}

export interface Finding {
  severity: string;
  category: string;
  description: string;
  location?: string;
  suggestion?: string;
}

export interface RewriteTarget {
  original: string;
  suggested: string;
  reason: string;
  priority: string;
}

export interface PrototypeAlignment {
  score: number;
  matched_rules: string[];
  unmatched_rules: string[];
  notes?: string;
}

export interface SemanticReviewResponse {
  task_id: string;
  passed: boolean;
  severity_summary: SeveritySummary;
  findings: Finding[];
  rewrite_target: RewriteTarget[];
  prototype_alignment?: PrototypeAlignment;
}

// ============ Article Workflow Types ============

export interface ArticleWorkflowOpinionInput {
  evidence_bundle: EvidenceBundle;
  audience: string;
  thesis_hint?: string;
  context_metadata?: Record<string, unknown>;
}

export interface ArticleWorkflowReviewInput {
  audience: string;
  prototype_hint?: string;
  register?: string;
  context_metadata?: Record<string, unknown>;
  // 注意：不暴露 content 字段，由工作流自动生成
}

export interface ArticleWorkflowInputData {
  opinion: ArticleWorkflowOpinionInput;
  semantic_review: ArticleWorkflowReviewInput;
}

export interface ArticleWorkflowRequest {
  input_data: ArticleWorkflowInputData;
  // 注意：不暴露顶层 metadata 字段
}

export interface ChildTaskResult {
  module_name: string;
  task_id: string;
  status: string;
  result?: Record<string, unknown>;
  error?: string;
}

export interface ArticleWorkflowResponse {
  task_id: string;
  child_task_ids: string[];
  status: string;
  result?: Record<string, unknown>;
  child_results: ChildTaskResult[];
  prototype_alignment?: PrototypeAlignment;
  errors: string[];
}

// ============ Error Response ============

export interface ApiErrorResponse {
  detail: string;
}