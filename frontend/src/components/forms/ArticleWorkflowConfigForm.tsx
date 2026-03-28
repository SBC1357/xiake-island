/**
 * Article Workflow Config Form
 * 
 * 文章工作流配置表单
 * 
 * 重要边界：
 * - 不暴露 semantic_review.content 手填字段
 * - 不暴露顶层 metadata 配置入口
 */

import { useState, useCallback, useMemo } from 'react';
import { Card, CardHeader, CardBody, Input, Textarea, Select } from '../ui';
import { EvidenceBundleEditor, type EvidenceBundleData } from '../EvidenceBundleEditor';
import { ContextMetadataEditor } from '../ContextMetadataEditor';
import type { 
  ArticleDraftConfig, 
  ArticleWorkflowRequest,
  ReviewAudienceMode 
} from '../../types';

export interface ArticleWorkflowConfigFormProps {
  value: ArticleDraftConfig;
  onChange: (value: ArticleDraftConfig) => void;
  onSubmit: (request: ArticleWorkflowRequest) => void;
  disabled?: boolean;
}

export function ArticleWorkflowConfigForm({ value, onChange, onSubmit, disabled }: ArticleWorkflowConfigFormProps) {
  const [opinionContextMetadata, setOpinionContextMetadata] = useState<Record<string, unknown> | null>(null);
  const [reviewContextMetadata, setReviewContextMetadata] = useState<Record<string, unknown> | null>(null);
  
  // ========== Opinion 部分 ==========
  
  const handleOpinionAudienceChange = useCallback((opinionAudience: string) => {
    onChange({ ...value, opinionAudience });
  }, [value, onChange]);
  
  const handleEvidenceChange = useCallback((evidence: EvidenceBundleData) => {
    onChange({
      ...value,
      evidenceItems: evidence.items,
      evidenceSummary: evidence.summary || '',
    });
  }, [value, onChange]);
  
  const handleThesisHintChange = useCallback((thesisHint: string) => {
    onChange({ ...value, thesisHint });
  }, [value, onChange]);
  
  const handleOpinionContextMetadataTextChange = useCallback((text: string) => {
    onChange({ ...value, opinionContextMetadataText: text });
  }, [value, onChange]);
  
  // ========== Review 部分 ==========
  
  const handleReviewAudienceModeChange = useCallback((mode: ReviewAudienceMode) => {
    onChange({ ...value, reviewAudienceMode: mode });
  }, [value, onChange]);
  
  const handleReviewAudienceChange = useCallback((reviewAudience: string) => {
    onChange({ ...value, reviewAudience });
  }, [value, onChange]);
  
  const handlePrototypeHintChange = useCallback((prototypeHint: string) => {
    onChange({ ...value, prototypeHint });
  }, [value, onChange]);
  
  const handleRegisterChange = useCallback((register: string) => {
    onChange({ ...value, register });
  }, [value, onChange]);
  
  const handleReviewContextMetadataTextChange = useCallback((text: string) => {
    onChange({ ...value, reviewContextMetadataText: text });
  }, [value, onChange]);
  
  // 计算实际使用的审核受众
  const effectiveReviewAudience = useMemo(() => {
    return value.reviewAudienceMode === 'use_opinion' 
      ? value.opinionAudience 
      : value.reviewAudience;
  }, [value.reviewAudienceMode, value.opinionAudience, value.reviewAudience]);
  
  const buildRequest = useCallback((): ArticleWorkflowRequest => {
    return {
      input_data: {
        opinion: {
          evidence_bundle: {
            items: value.evidenceItems.map(item => ({
              id: item.id,
              content: item.content,
              source: item.source,
              relevance: item.relevance,
            })),
            summary: value.evidenceSummary || undefined,
          },
          audience: value.opinionAudience,
          thesis_hint: value.thesisHint || undefined,
          context_metadata: opinionContextMetadata || undefined,
        },
        semantic_review: {
          // 注意：不暴露 content 字段，由工作流自动生成
          audience: effectiveReviewAudience,
          prototype_hint: value.prototypeHint || undefined,
          register: value.register || undefined,
          context_metadata: reviewContextMetadata || undefined,
        },
      },
      // 注意：不暴露顶层 metadata
    };
  }, [value, opinionContextMetadata, reviewContextMetadata, effectiveReviewAudience]);
  
  const handleSubmit = useCallback(() => {
    const request = buildRequest();
    onSubmit(request);
  }, [buildRequest, onSubmit]);
  
  const isValid = value.opinionAudience.trim() !== '' && 
    value.evidenceItems.some(item => item.content.trim() !== '') &&
    effectiveReviewAudience.trim() !== '';
  
  return (
    <div className="space-y-6">
      {/* Opinion 部分 */}
      <Card>
        <CardHeader>
          <h3 className="text-sm font-medium text-gray-900">观点生成配置</h3>
        </CardHeader>
        <CardBody className="space-y-4">
          <Input
            label="观点受众"
            value={value.opinionAudience}
            onChange={(e) => handleOpinionAudienceChange(e.target.value)}
            placeholder="例如：医学专业人士、患者、大众..."
            required
            disabled={disabled}
          />
          <Textarea
            label="观点提示"
            value={value.thesisHint}
            onChange={(e) => handleThesisHintChange(e.target.value)}
            placeholder="可选：提供观点生成的方向或提示..."
            rows={2}
            disabled={disabled}
          />
        </CardBody>
      </Card>
      
      <EvidenceBundleEditor
        value={{
          items: value.evidenceItems,
          summary: value.evidenceSummary || undefined,
        }}
        onChange={handleEvidenceChange}
        disabled={disabled}
      />
      
      <ContextMetadataEditor
        value={value.opinionContextMetadataText}
        onChange={handleOpinionContextMetadataTextChange}
        onParsed={setOpinionContextMetadata}
        disabled={disabled}
      />
      
      {/* Review 部分 */}
      <Card>
        <CardHeader>
          <h3 className="text-sm font-medium text-gray-900">语义审核配置</h3>
        </CardHeader>
        <CardBody className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-md p-3 mb-4">
            <p className="text-sm text-blue-700">
              <strong>说明：</strong>审核内容由工作流自动从观点生成结果中提取，无需手动填写。
            </p>
          </div>
          
          <Select
            label="审核受众设置"
            value={value.reviewAudienceMode}
            onChange={(e) => handleReviewAudienceModeChange(e.target.value as ReviewAudienceMode)}
            options={[
              { value: 'use_opinion', label: '沿用观点受众' },
              { value: 'separate', label: '单独设置审核受众' },
            ]}
            disabled={disabled}
          />
          
          {value.reviewAudienceMode === 'separate' && (
            <Input
              label="审核受众"
              value={value.reviewAudience}
              onChange={(e) => handleReviewAudienceChange(e.target.value)}
              placeholder="例如：医学专业人士、患者、大众..."
              required
              disabled={disabled}
            />
          )}
          
          {value.reviewAudienceMode === 'use_opinion' && (
            <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
              <p className="text-sm text-gray-600">
                当前将使用观点受众：<strong>{value.opinionAudience}</strong>
              </p>
            </div>
          )}
          
          <Input
            label="原型提示"
            value={value.prototypeHint}
            onChange={(e) => handlePrototypeHintChange(e.target.value)}
            placeholder='可选：例如"通俗易懂"、"学术严谨"...'
            disabled={disabled}
          />
          
          <Input
            label="语体要求"
            value={value.register}
            onChange={(e) => handleRegisterChange(e.target.value)}
            placeholder='可选：例如"正式"、"口语化"...'
            disabled={disabled}
          />
        </CardBody>
      </Card>
      
      <ContextMetadataEditor
        value={value.reviewContextMetadataText}
        onChange={handleReviewContextMetadataTextChange}
        onParsed={setReviewContextMetadata}
        disabled={disabled}
      />
      
      <div className="flex justify-end pt-2">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={disabled || !isValid}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          执行文章工作流
        </button>
      </div>
    </div>
  );
}