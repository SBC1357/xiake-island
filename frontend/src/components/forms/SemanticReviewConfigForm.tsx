/**
 * Semantic Review Config Form
 * 
 * 语义审核配置表单
 */

import { useState, useCallback } from 'react';
import { Card, CardBody, Input, Textarea } from '../ui';
import { ContextMetadataEditor } from '../ContextMetadataEditor';
import type { SemanticReviewDraftConfig, SemanticReviewRequest } from '../../types';

export interface SemanticReviewConfigFormProps {
  value: SemanticReviewDraftConfig;
  onChange: (value: SemanticReviewDraftConfig) => void;
  onSubmit: (request: SemanticReviewRequest) => void;
  disabled?: boolean;
}

export function SemanticReviewConfigForm({ value, onChange, onSubmit, disabled }: SemanticReviewConfigFormProps) {
  const [contextMetadata, setContextMetadata] = useState<Record<string, unknown> | null>(null);
  
  const handleContentChange = useCallback((content: string) => {
    onChange({ ...value, content });
  }, [value, onChange]);
  
  const handleAudienceChange = useCallback((audience: string) => {
    onChange({ ...value, audience });
  }, [value, onChange]);
  
  const handlePrototypeHintChange = useCallback((prototypeHint: string) => {
    onChange({ ...value, prototypeHint });
  }, [value, onChange]);
  
  const handleRegisterChange = useCallback((register: string) => {
    onChange({ ...value, register });
  }, [value, onChange]);
  
  const handleContextMetadataTextChange = useCallback((text: string) => {
    onChange({ ...value, contextMetadataText: text });
  }, [value, onChange]);
  
  const handleContextMetadataParsed = useCallback((parsed: Record<string, unknown> | null) => {
    setContextMetadata(parsed);
  }, []);
  
  const buildRequest = useCallback((): SemanticReviewRequest => {
    return {
      content: value.content,
      audience: value.audience,
      prototype_hint: value.prototypeHint || undefined,
      register: value.register || undefined,
      context_metadata: contextMetadata || undefined,
    };
  }, [value, contextMetadata]);
  
  const handleSubmit = useCallback(() => {
    const request = buildRequest();
    onSubmit(request);
  }, [buildRequest, onSubmit]);
  
  const isValid = value.content.trim() !== '' && value.audience.trim() !== '';
  const contentWarning = value.content.trim().length > 0 && value.content.trim().length < 50;
  
  return (
    <div className="space-y-4">
      <Card>
        <CardBody className="space-y-4">
          <Textarea
            label="待审核内容"
            value={value.content}
            onChange={(e) => handleContentChange(e.target.value)}
            placeholder="输入需要审核的中文内容..."
            rows={8}
            required
            disabled={disabled}
            error={contentWarning ? '内容过短可能影响审核效果，建议至少50字' : undefined}
          />
          <Input
            label="目标受众"
            value={value.audience}
            onChange={(e) => handleAudienceChange(e.target.value)}
            placeholder="例如：医学专业人士、患者、大众..."
            required
            disabled={disabled}
          />
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
        value={value.contextMetadataText}
        onChange={handleContextMetadataTextChange}
        onParsed={handleContextMetadataParsed}
        disabled={disabled}
      />
      
      <div className="flex justify-end pt-2">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={disabled || !isValid}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          执行语义审核
        </button>
      </div>
    </div>
  );
}