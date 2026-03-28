/**
 * Evidence Bundle Editor
 * 
 * 证据包编辑器，支持添加/删除/编辑证据项 + 文件上传
 */

import { useCallback, useState, useRef } from 'react';
import { Card, CardHeader, CardBody, Button, Input, Textarea, Badge, Spinner } from './ui';
import { uploadEvidenceFile, type UploadResponse, type TraceableEvidence } from '../api/upload';

export interface EvidenceItemData {
  id: string;
  content: string;
  source?: string;
  relevance?: number;
  /** 来自文件上传的证据 */
  fromUpload?: boolean;
  uploadId?: string;
}

export interface EvidenceBundleData {
  items: EvidenceItemData[];
  summary?: string;
}

export interface EvidenceBundleEditorProps {
  value: EvidenceBundleData;
  onChange: (value: EvidenceBundleData) => void;
  disabled?: boolean;
  taskId?: string;
}

function generateItemId(): string {
  return `e${Date.now().toString(36)}${Math.random().toString(36).slice(2, 5)}`;
}

export function EvidenceBundleEditor({ value, onChange, disabled, taskId }: EvidenceBundleEditorProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAddItem = useCallback(() => {
    onChange({
      ...value,
      items: [...value.items, { id: generateItemId(), content: '', source: '', relevance: undefined }],
    });
  }, [value, onChange]);
  
  const handleRemoveItem = useCallback((index: number) => {
    const newItems = value.items.filter((_, i) => i !== index);
    onChange({ ...value, items: newItems });
  }, [value, onChange]);
  
  const handleItemChange = useCallback((index: number, field: keyof EvidenceItemData, fieldValue: string | number | undefined) => {
    const newItems = value.items.map((item, i) => {
      if (i === index) {
        return { ...item, [field]: fieldValue };
      }
      return item;
    });
    onChange({ ...value, items: newItems });
  }, [value, onChange]);
  
  const handleSummaryChange = useCallback((summary: string) => {
    onChange({ ...value, summary });
  }, [value, onChange]);

  const handleFileUpload = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    setUploadError(null);
    try {
      for (const file of Array.from(files)) {
        const result: UploadResponse = await uploadEvidenceFile(file, taskId);
        if (result.status === 'completed' && result.evidences) {
          const newItems: EvidenceItemData[] = result.evidences.map((ev: TraceableEvidence) => ({
            id: generateItemId(),
            content: ev.content,
            source: `${file.name} (p${ev.source_pages?.join(',') || '?'})`,
            relevance: ev.confidence,
            fromUpload: true,
            uploadId: result.upload_id,
          }));
          onChange({
            ...value,
            items: [...value.items, ...newItems],
          });
        } else {
          setUploadError(`文件 ${file.name} 处理未完成: ${result.status}`);
        }
      }
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : '上传失败');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  }, [value, onChange, taskId]);
  
  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-900">证据包</h3>
        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled || uploading}
          >
            {uploading ? <><Spinner size="sm" /> 识别中...</> : '📎 上传文件'}
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.pptx,.jpg,.jpeg,.png"
            multiple
            className="hidden"
            onChange={(e) => handleFileUpload(e.target.files)}
          />
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleAddItem}
            disabled={disabled}
          >
            + 添加证据
          </Button>
        </div>
      </CardHeader>
      <CardBody className="space-y-4">
        {uploadError && (
          <div className="p-2 bg-red-50 border border-red-200 rounded text-xs text-red-600">
            {uploadError}
          </div>
        )}
        {value.items.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-4">
            暂无证据项，点击"添加证据"开始添加
          </p>
        ) : (
          value.items.map((item, index) => (
            <div key={item.id} className="border border-gray-200 rounded-md p-3 space-y-3">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500 font-mono">证据 #{index + 1}</span>
                  {item.fromUpload && <Badge variant="info" size="sm">文件识别</Badge>}
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemoveItem(index)}
                  disabled={disabled}
                  className="text-red-600 hover:text-red-700"
                >
                  删除
                </Button>
              </div>
              <Textarea
                label="证据内容"
                value={item.content}
                onChange={(e) => handleItemChange(index, 'content', e.target.value)}
                placeholder="输入证据内容..."
                rows={3}
                required
                disabled={disabled}
              />
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="证据来源"
                  value={item.source || ''}
                  onChange={(e) => handleItemChange(index, 'source', e.target.value)}
                  placeholder="可选"
                  disabled={disabled}
                />
                <Input
                  label="相关性 (0-1)"
                  type="number"
                  min={0}
                  max={1}
                  step={0.1}
                  value={item.relevance !== undefined ? item.relevance : ''}
                  onChange={(e) => handleItemChange(index, 'relevance', e.target.value ? parseFloat(e.target.value) : undefined)}
                  placeholder="可选"
                  disabled={disabled}
                />
              </div>
            </div>
          ))
        )}
        <Textarea
          label="证据摘要"
          value={value.summary || ''}
          onChange={(e) => handleSummaryChange(e.target.value)}
          placeholder="可选：输入证据整体摘要..."
          rows={2}
          disabled={disabled}
        />
      </CardBody>
    </Card>
  );
}