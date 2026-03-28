/**
 * Drafting Panel
 * 
 * SP-7D: 成稿面板 - 将写作指令(prompt)转换为正文内容
 * 
 * Backend Contract: POST /v1/drafting/generate
 */

import { useState, useCallback } from 'react';
import { Card, CardHeader, CardBody, Button, Badge, Spinner } from './ui';
import { executeDrafting, ApiError } from '../api/drafting';
import type { DraftingResult, CompiledPromptResponse } from '../types';

interface DraftingPanelProps {
  writingResult?: CompiledPromptResponse;
  onDraftingComplete?: (result: DraftingResult) => void;
  disabled?: boolean;
}

export function DraftingPanel({
  writingResult,
  onDraftingComplete,
  disabled = false,
}: DraftingPanelProps) {
  const [draftingResult, setDraftingResult] = useState<DraftingResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDraft = useCallback(async () => {
    if (!writingResult) return;

    setLoading(true);
    setError(null);

    try {
      // 匹配后端 DraftingRequest (extra="forbid")
      const result = await executeDrafting({
        system_prompt: writingResult.system_prompt,
        user_prompt: writingResult.user_prompt,
      });

      setDraftingResult(result);
      onDraftingComplete?.(result);
    } catch (e) {
      const message = e instanceof ApiError ? e.message : '成稿失败';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [writingResult, onDraftingComplete]);

  if (!writingResult) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900">成稿</h3>
            <Badge variant="default">待执行</Badge>
          </div>
        </CardHeader>
        <CardBody>
          <p className="text-sm text-gray-500">请先完成写作指令编译</p>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900">成稿</h3>
          {draftingResult ? (
            <Badge variant="success">已完成</Badge>
          ) : (
            <Badge variant="info">待执行</Badge>
          )}
        </div>
      </CardHeader>
      <CardBody className="space-y-4">
        {/* 写作指令摘要 */}
        <div className="p-2 bg-gray-50 rounded">
          <p className="text-xs text-gray-500 mb-1">基于写作指令</p>
          <div className="flex items-center gap-2 text-xs">
            <Badge variant="default">System: {writingResult.system_prompt.length} 字符</Badge>
            <Badge variant="default">User: {writingResult.user_prompt.length} 字符</Badge>
          </div>
        </div>

        {/* 错误信息 */}
        {error && (
          <div className="p-2 bg-red-50 border border-red-200 rounded">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* 成稿按钮 */}
        <Button
          onClick={handleDraft}
          disabled={disabled || loading || !!draftingResult}
          className="w-full"
        >
          {loading ? <Spinner size="sm" /> : draftingResult ? '已生成成稿' : '生成正文成稿'}
        </Button>

        {/* 成稿结果 */}
        {draftingResult && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Task ID</span>
              <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                {draftingResult.task_id.slice(0, 8)}...
              </code>
            </div>

            {/* 元信息 */}
            <div className="flex items-center gap-4 text-sm">
              <span>
                字数: <Badge variant="default">{draftingResult.word_count}</Badge>
              </span>
              {draftingResult.trace?.generation_mode && (
                <span>
                  模式: <Badge variant="default">{draftingResult.trace.generation_mode}</Badge>
                </span>
              )}
            </div>

            {/* 正文预览 */}
            <div>
              <p className="text-xs text-gray-500 mb-1">正文成稿预览</p>
              <div className="p-2 bg-gray-50 rounded max-h-[200px] overflow-y-auto">
                <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                  {draftingResult.content.slice(0, 500)}
                  {draftingResult.content.length > 500 && '...'}
                </pre>
              </div>
            </div>

            <p className="text-xs text-gray-500">
              正文成稿已生成，可继续进行质量审核
            </p>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
