/**
 * Draft Storage Hook Tests
 * 
 * 覆盖 clearDraft 和 resetToDefault 的区分
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useDraftStorage } from '../hooks/useDraftStorage';
import type { OpinionDraftConfig, ArticleDraftConfig } from '../types/draft';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('useDraftStorage', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  describe('clearDraft vs resetToDefault', () => {
    it('clearDraft 应该返回真正的空白草稿（无预填值）', () => {
      const { result } = renderHook(() => useDraftStorage<OpinionDraftConfig>('opinion'));
      
      act(() => {
        result.current.clearDraft();
      });
      
      // clearDraft 应该返回空白草稿，所有字段为空
      const draft = result.current.draft as OpinionDraftConfig;
      expect(draft.audience).toBe('');
      expect(draft.evidenceItems).toEqual([]);
      expect(draft.evidenceSummary).toBe('');
      expect(draft.thesisHint).toBe('');
      expect(draft.contextMetadataText).toBe('');
      expect(result.current.isDirty).toBe(false);
    });

    it('resetToDefault 应该返回系统默认草稿（有预填值）', () => {
      const { result } = renderHook(() => useDraftStorage<OpinionDraftConfig>('opinion'));
      
      act(() => {
        result.current.resetToDefault();
      });
      
      // resetToDefault 应该返回系统默认值
      const draft = result.current.draft as OpinionDraftConfig;
      expect(draft.audience).toBe('医学专业人士');
      expect(draft.evidenceItems).toHaveLength(1);
      expect(draft.evidenceItems[0].id).toBe('e1');
      expect(result.current.isDirty).toBe(false);
    });

    it('clearDraft 和 resetToDefault 应该产生不同的结果', () => {
      const { result } = renderHook(() => useDraftStorage<OpinionDraftConfig>('opinion'));
      
      // 先 clearDraft
      act(() => {
        result.current.clearDraft();
      });
      const clearedAudience = (result.current.draft as OpinionDraftConfig).audience;
      
      // 再 resetToDefault
      act(() => {
        result.current.resetToDefault();
      });
      const defaultAudience = (result.current.draft as OpinionDraftConfig).audience;
      
      // 两者应该不同
      expect(clearedAudience).toBe('');
      expect(defaultAudience).toBe('医学专业人士');
      expect(clearedAudience).not.toBe(defaultAudience);
    });

    it('article 目标的 clearDraft 应该返回空白草稿', () => {
      const { result } = renderHook(() => useDraftStorage<ArticleDraftConfig>('article'));
      
      act(() => {
        result.current.clearDraft();
      });
      
      const draft = result.current.draft as ArticleDraftConfig;
      expect(draft.opinionAudience).toBe('');
      expect(draft.evidenceItems).toEqual([]);
      expect(draft.reviewAudience).toBe('');
    });

    it('article 目标的 resetToDefault 应该返回预填值', () => {
      const { result } = renderHook(() => useDraftStorage<ArticleDraftConfig>('article'));
      
      act(() => {
        result.current.resetToDefault();
      });
      
      const draft = result.current.draft as ArticleDraftConfig;
      expect(draft.opinionAudience).toBe('医学专业人士');
      expect(draft.evidenceItems).toHaveLength(1);
      expect(draft.reviewAudienceMode).toBe('use_opinion');
    });
  });

  describe('草稿持久化', () => {
    it('保存草稿后应存储到 localStorage', () => {
      const { result } = renderHook(() => useDraftStorage<OpinionDraftConfig>('opinion'));
      
      act(() => {
        result.current.saveDraft({
          ...result.current.draft,
          audience: '测试受众',
        } as OpinionDraftConfig);
      });
      
      const stored = localStorageMock.getItem('xiakedao_draft_opinion');
      expect(stored).toBeTruthy();
      const parsed = JSON.parse(stored!);
      expect(parsed.audience).toBe('测试受众');
      expect(result.current.isDirty).toBe(true);
    });
  });
});