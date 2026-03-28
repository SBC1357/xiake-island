/**
 * Context Metadata Editor
 * 
 * 上下文元数据编辑器，支持 JSON 文本输入和解析
 * 
 * 重要约束：context_metadata 必须是 JSON 对象（plain object）
 * - 空文本：有效，表示不传递
 * - JSON 对象：有效
 * - 数组、字符串、数字、布尔值：无效
 */

import { useMemo, useCallback, useEffect, useRef } from 'react';
import { Card, CardHeader, CardBody, Textarea, Badge } from './ui';

export interface ContextMetadataEditorProps {
  value: string; // JSON 文本
  onChange: (value: string) => void;
  onParsed?: (parsed: Record<string, unknown> | null) => void;
  disabled?: boolean;
}

// 判断值是否为普通对象（非数组、非 null）
function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

interface ParseResult {
  parsed: Record<string, unknown> | null;
  error: string | null;
  isValidObject: boolean; // 是否为有效的对象类型
}

function parseJsonText(text: string): ParseResult {
  // 空文本：有效，表示不传递 context_metadata
  if (!text.trim()) {
    return { parsed: null, error: null, isValidObject: true };
  }
  
  try {
    const parsed = JSON.parse(text);
    
    // 检查是否为对象类型
    if (!isPlainObject(parsed)) {
      // 不是对象，根据类型给出具体错误提示
      const typeName = Array.isArray(parsed) ? '数组' :
                       typeof parsed === 'string' ? '字符串' :
                       typeof parsed === 'number' ? '数字' :
                       typeof parsed === 'boolean' ? '布尔值' :
                       'null';
      return { 
        parsed: null, 
        error: `类型错误：必须是 JSON 对象，当前是 ${typeName}`,
        isValidObject: false 
      };
    }
    
    // 是有效的对象
    return { parsed, error: null, isValidObject: true };
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'JSON 格式错误';
    return { parsed: null, error: errorMessage, isValidObject: false };
  }
}

export function ContextMetadataEditor({ value, onChange, onParsed, disabled }: ContextMetadataEditorProps) {
  // 使用 useMemo 计算解析结果，避免在 useEffect 中设置状态
  const { parsed, parseError, isValidObject } = useMemo(() => {
    const result = parseJsonText(value);
    return { 
      parsed: result.parsed, 
      parseError: result.error, 
      isValidObject: result.isValidObject 
    };
  }, [value]);
  
// 跟踪上次通知的值，避免重复调用 onParsed
  const lastNotifiedRef = useRef<{ parsedJsonStr: string | null }>({ parsedJsonStr: null });
  
  // 当解析结果变化时通知父组件
  useEffect(() => {
    const parsedJsonStr = parsed !== null ? JSON.stringify(parsed) : null;
    
    // 只有在值真正变化时才通知
    if (parsedJsonStr !== lastNotifiedRef.current.parsedJsonStr) {
      lastNotifiedRef.current.parsedJsonStr = parsedJsonStr;
      onParsed?.(parsed);
    }
  }, [parsed, onParsed]);
  
  const handleChange = useCallback((text: string) => {
    onChange(text);
  }, [onChange]);
  
  const handleFormat = useCallback(() => {
    if (!value.trim()) return;
    
    try {
      const parsedValue = JSON.parse(value);
      // 只有对象才格式化
      if (isPlainObject(parsedValue)) {
        const formatted = JSON.stringify(parsedValue, null, 2);
        onChange(formatted);
      }
    } catch {
      // 格式化失败，保持原样
    }
  }, [value, onChange]);
  
  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium text-gray-900">上下文元数据</h3>
          {value.trim() && isValidObject && !parseError && (
            <Badge variant="success" size="sm">JSON 对象有效</Badge>
          )}
          {parseError && (
            <Badge variant="danger" size="sm">无效</Badge>
          )}
        </div>
        <button
          type="button"
          onClick={handleFormat}
          disabled={disabled || !value.trim()}
          className="text-xs text-blue-600 hover:text-blue-700 disabled:text-gray-400"
        >
          格式化
        </button>
      </CardHeader>
      <CardBody>
        <Textarea
          value={value}
          onChange={(e) => handleChange(e.target.value)}
          placeholder='可选：输入 JSON 对象格式的上下文元数据，例如：&#10;{&#10;  "department": "心内科",&#10;  "disease_type": "冠心病"&#10;}&#10;&#10;注意：必须是 JSON 对象，不能是数组、字符串或数字。'
          rows={6}
          disabled={disabled}
          className="font-mono text-sm"
        />
        {parseError && (
          <p className="mt-2 text-sm text-red-600">
            {parseError}
          </p>
        )}
        <p className="mt-2 text-xs text-gray-500">
          留空表示不传递上下文元数据。输入值必须是 JSON 对象（不能是数组、字符串或数字）。
        </p>
      </CardBody>
    </Card>
  );
}