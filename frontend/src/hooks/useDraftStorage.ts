/**
 * Draft Storage Hook
 * 
 * 管理 localStorage 中的草稿数据
 */

import { useState, useEffect, useCallback } from 'react';
import type { TargetId } from '../types';
import {
  getDraftStorageKey,
  DEFAULT_OPINION_DRAFT,
  DEFAULT_SEMANTIC_REVIEW_DRAFT,
  DEFAULT_ARTICLE_DRAFT,
  DEFAULT_STANDARD_CHAIN_DRAFT,
  EMPTY_OPINION_DRAFT,
  EMPTY_SEMANTIC_REVIEW_DRAFT,
  EMPTY_ARTICLE_DRAFT,
  EMPTY_STANDARD_CHAIN_DRAFT,
  type OpinionDraftConfig,
  type SemanticReviewDraftConfig,
  type ArticleDraftConfig,
  type StandardChainDraftConfig,
} from '../types';

type DraftConfig = OpinionDraftConfig | SemanticReviewDraftConfig | ArticleDraftConfig | StandardChainDraftConfig;

function getDefaultDraft(targetId: TargetId): DraftConfig {
  switch (targetId) {
    case 'opinion':
      return DEFAULT_OPINION_DRAFT;
    case 'semantic_review':
      return DEFAULT_SEMANTIC_REVIEW_DRAFT;
    case 'article':
      return DEFAULT_ARTICLE_DRAFT;
    case 'standard_chain':
      return DEFAULT_STANDARD_CHAIN_DRAFT;
    default:
      throw new Error(`Unknown target: ${targetId}`);
  }
}

function getEmptyDraft(targetId: TargetId): DraftConfig {
  switch (targetId) {
    case 'opinion':
      return EMPTY_OPINION_DRAFT;
    case 'semantic_review':
      return EMPTY_SEMANTIC_REVIEW_DRAFT;
    case 'article':
      return EMPTY_ARTICLE_DRAFT;
    case 'standard_chain':
      return EMPTY_STANDARD_CHAIN_DRAFT;
    default:
      throw new Error(`Unknown target: ${targetId}`);
  }
}

export function useDraftStorage<T extends DraftConfig>(targetId: TargetId) {
  const storageKey = getDraftStorageKey(targetId);
  
  const [draft, setDraft] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        return JSON.parse(stored) as T;
      }
    } catch (e) {
      console.error('Failed to load draft:', e);
    }
    return getDefaultDraft(targetId) as T;
  });
  
  const [isDirty, setIsDirty] = useState(false);
  
  // 保存草稿到 localStorage
  const saveDraft = useCallback((config: T) => {
    setDraft(config);
    setIsDirty(true);
    try {
      localStorage.setItem(storageKey, JSON.stringify(config));
    } catch (e) {
      console.error('Failed to save draft:', e);
    }
  }, [storageKey]);
  
  // 清空当前草稿（重置为真正的空白可编辑态）
  const clearDraft = useCallback(() => {
    const emptyDraft = getEmptyDraft(targetId) as T;
    setDraft(emptyDraft);
    setIsDirty(false);
    localStorage.removeItem(storageKey);
  }, [targetId, storageKey]);
  
  // 恢复系统默认（预填常用值）
  const resetToDefault = useCallback(() => {
    const defaultDraft = getDefaultDraft(targetId) as T;
    setDraft(defaultDraft);
    setIsDirty(false);
    localStorage.removeItem(storageKey);
  }, [targetId, storageKey]);
  
  // 同步 draft 到 localStorage（当 draft 变化时）
  useEffect(() => {
    if (isDirty) {
      localStorage.setItem(storageKey, JSON.stringify(draft));
    }
  }, [draft, isDirty, storageKey]);
  
  return {
    draft,
    setDraft,
    saveDraft,
    clearDraft,
    resetToDefault,
    isDirty,
  };
}