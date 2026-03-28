/**
 * Opinion Config Form
 * 
 * 观点生成配置表单
 */

import { useState, useCallback } from 'react';
import { Card, CardBody, Input, Textarea } from '../ui';
import { EvidenceBundleEditor, type EvidenceBundleData } from '../EvidenceBundleEditor';
import { ContextMetadataEditor } from '../ContextMetadataEditor';
import type { OpinionDraftConfig, OpinionGenerateRequest } from '../../types';

export interface OpinionConfigFormProps {
  value: OpinionDraftConfig;
  onChange: (value: OpinionDraftConfig) => void;
  onSubmit: (request: OpinionGenerateRequest) => void;
  disabled?: boolean;
}

export function OpinionConfigForm({ value, onChange, onSubmit, disabled }: OpinionConfigFormProps) {
  const [contextMetadata, setContextMetadata] = useState<Record<string, unknown> | null>(null);
  
  const handleAudienceChange = useCallback((audience: string) => {
    onChange({ ...value, audience });
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
  
  const handleContextMetadataTextChange = useCallback((text: string) => {
    onChange({ ...value, contextMetadataText: text });
  }, [value, onChange]);
  
  const handleContextMetadataParsed = useCallback((parsed: Record<string, unknown> | null) => {
    setContextMetadata(parsed);
  }, []);
  
  const buildRequest = useCallback((): OpinionGenerateRequest => {
    return {
      evidence_bundle: {
        items: value.evidenceItems.map(item => ({
          id: item.id,
          content: item.content,
          source: item.source,
          relevance: item.relevance,
        })),
        summary: value.evidenceSummary || undefined,
      },
      audience: value.audience,
      thesis_hint: value.thesisHint || undefined,
      context_metadata: contextMetadata || undefined,
    };
  }, [value, contextMetadata]);
  
  const handleSubmit = useCallback(() => {
    const request = buildRequest();
    onSubmit(request);
  }, [buildRequest, onSubmit]);
  
  const isValid = value.audience.trim() !== '' && 
    value.evidenceItems.some(item => item.content.trim() !== '');
  
  return (
    <div className="space-y-4">
      <Card>
        <CardBody className="space-y-4">
          <Input
            label="目标受众"
            value={value.audience}
            onChange={(e) => handleAudienceChange(e.target.value)}
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
          执行观点生成
        </button>
      </div>
    </div>
  );
}