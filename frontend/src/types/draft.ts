/**
 * Draft Types
 * 
 * 草稿配置模型
 */

import type { TargetId } from './target';

// ============ Opinion Draft Config ============

export interface OpinionDraftConfig {
  audience: string;
  evidenceItems: Array<{
    id: string;
    content: string;
    source?: string;
    relevance?: number;
  }>;
  evidenceSummary: string;
  thesisHint: string;
  contextMetadataText: string; // UI 辅助字段，提交前解析
}

// 系统默认值（预填常用值）
export const DEFAULT_OPINION_DRAFT: OpinionDraftConfig = {
  audience: '医学专业人士',
  evidenceItems: [
    { id: 'e1', content: '', source: '', relevance: undefined },
  ],
  evidenceSummary: '',
  thesisHint: '',
  contextMetadataText: '',
};

// 空白草稿（清空后状态）
export const EMPTY_OPINION_DRAFT: OpinionDraftConfig = {
  audience: '',
  evidenceItems: [],
  evidenceSummary: '',
  thesisHint: '',
  contextMetadataText: '',
};

// ============ Semantic Review Draft Config ============

export interface SemanticReviewDraftConfig {
  content: string;
  audience: string;
  prototypeHint: string;
  register: string;
  contextMetadataText: string;
}

// 系统默认值
export const DEFAULT_SEMANTIC_REVIEW_DRAFT: SemanticReviewDraftConfig = {
  content: '',
  audience: '医学专业人士',
  prototypeHint: '',
  register: '',
  contextMetadataText: '',
};

// 空白草稿
export const EMPTY_SEMANTIC_REVIEW_DRAFT: SemanticReviewDraftConfig = {
  content: '',
  audience: '',
  prototypeHint: '',
  register: '',
  contextMetadataText: '',
};

// ============ Article Draft Config ============

export type ReviewAudienceMode = 'use_opinion' | 'separate';

export interface ArticleDraftConfig {
  // Opinion 部分
  opinionAudience: string;
  evidenceItems: Array<{
    id: string;
    content: string;
    source?: string;
    relevance?: number;
  }>;
  evidenceSummary: string;
  thesisHint: string;
  opinionContextMetadataText: string;
  
  // Review 部分
  reviewAudienceMode: ReviewAudienceMode; // UI 辅助字段
  reviewAudience: string;
  prototypeHint: string;
  register: string;
  reviewContextMetadataText: string;
}

// ============ Standard Chain Draft Config ============

export interface StandardChainDraftConfig {
  selectedFacts: Array<{
    fact_id: string;
    domain: string;
    fact_key: string;
    value: string;
  }>;
  productId: string;
  audience: string;
}

export const DEFAULT_STANDARD_CHAIN_DRAFT: StandardChainDraftConfig = {
  selectedFacts: [],
  productId: '',
  audience: '医学专业人士',
};

export const EMPTY_STANDARD_CHAIN_DRAFT: StandardChainDraftConfig = {
  selectedFacts: [],
  productId: '',
  audience: '',
};

// 系统默认值
export const DEFAULT_ARTICLE_DRAFT: ArticleDraftConfig = {
  opinionAudience: '医学专业人士',
  evidenceItems: [
    { id: 'e1', content: '', source: '', relevance: undefined },
  ],
  evidenceSummary: '',
  thesisHint: '',
  opinionContextMetadataText: '',
  reviewAudienceMode: 'use_opinion',
  reviewAudience: '医学专业人士',
  prototypeHint: '',
  register: '',
  reviewContextMetadataText: '',
};

// 空白草稿
export const EMPTY_ARTICLE_DRAFT: ArticleDraftConfig = {
  opinionAudience: '',
  evidenceItems: [],
  evidenceSummary: '',
  thesisHint: '',
  opinionContextMetadataText: '',
  reviewAudienceMode: 'use_opinion',
  reviewAudience: '',
  prototypeHint: '',
  register: '',
  reviewContextMetadataText: '',
};

// ============ Trigger Draft ============

export type DraftScope = 'browser_local';
export type StorageMode = 'localStorage';

export interface TriggerDraft<T = OpinionDraftConfig | SemanticReviewDraftConfig | ArticleDraftConfig> {
  targetId: TargetId;
  config: T;
  draftScope: DraftScope;
  storageMode: StorageMode;
  uiOnly: {
    formExpanded: boolean;
    lastEditedAt: string | null;
  };
  isDirty: boolean;
}

// ============ Draft Storage Key ============

export function getDraftStorageKey(targetId: TargetId): string {
  return `xiakedao_draft_${targetId}`;
}