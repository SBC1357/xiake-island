/**
 * Result Actions
 *
 * 结果视图通用操作组件：复制、导出 Markdown、提交反馈
 */

import { useState, useCallback } from 'react';
import { Button } from './Button';
import { FeedbackForm } from '../FeedbackForm';

export interface ResultActionsProps {
  /** 结果数据 */
  data: Record<string, unknown>;
  /** 任务ID */
  taskId: string;
  /** 模块名称 */
  moduleName: string;
}

export function ResultActions({ data, taskId, moduleName }: ResultActionsProps) {
  const [copied, setCopied] = useState(false);
  const [exported, setExported] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);

  // 复制为 JSON
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      console.error('Failed to copy:', e);
    }
  }, [data]);

  // 导出为 Markdown
  const handleExportMarkdown = useCallback(() => {
    const markdown = convertToMarkdown(data, moduleName, taskId);
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${moduleName}-${taskId.slice(0, 8)}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setExported(true);
    setTimeout(() => setExported(false), 2000);
  }, [data, moduleName, taskId]);

  return (
    <div className="pt-2 border-t border-gray-100 mt-4 space-y-2">
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleCopy}
        >
          {copied ? '已复制' : '复制结果'}
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleExportMarkdown}
        >
          {exported ? '已导出' : '导出 Markdown'}
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowFeedback(!showFeedback)}
        >
          {showFeedback ? '收起反馈' : '提交反馈'}
        </Button>
      </div>
      
      {showFeedback && (
        <FeedbackForm 
          taskId={taskId}
          onSuccess={() => setShowFeedback(false)}
        />
      )}
    </div>
  );
}

/**
 * 将结果数据转换为 Markdown 格式
 */
function convertToMarkdown(data: Record<string, unknown>, moduleName: string, taskId: string): string {
  const lines: string[] = [];

  lines.push(`# ${getModuleLabel(moduleName)} 结果`);
  lines.push('');
  lines.push(`> 任务ID: \`${taskId}\``);
  lines.push(`> 生成时间: ${new Date().toLocaleString('zh-CN')}`);
  lines.push('');

  if (moduleName === 'opinion') {
    lines.push(...convertOpinionToMarkdown(data));
  } else if (moduleName === 'semantic_review') {
    lines.push(...convertSemanticReviewToMarkdown(data));
  } else if (moduleName === 'orchestrator') {
    lines.push(...convertWorkflowToMarkdown(data));
  } else {
    // 默认：转换为 JSON 代码块
    lines.push('```json');
    lines.push(JSON.stringify(data, null, 2));
    lines.push('```');
  }

  return lines.join('\n');
}

function getModuleLabel(module: string): string {
  const labels: Record<string, string> = {
    opinion: '观点生成',
    semantic_review: '语义审核',
    orchestrator: '工作流',
  };
  return labels[module] || module;
}

function convertOpinionToMarkdown(data: Record<string, unknown>): string[] {
  const lines: string[] = [];
  const thesis = data.thesis as Record<string, unknown> | undefined;
  const supportPoints = data.support_points as Array<Record<string, unknown>> | undefined;
  const confidenceNotes = data.confidence_notes as Record<string, unknown> | undefined;

  // 核心观点
  if (thesis) {
    lines.push('## 核心观点');
    lines.push('');
    lines.push(thesis.statement as string);
    lines.push('');

    const confidence = thesis.confidence as number;
    if (confidence !== undefined) {
      lines.push(`**置信度**: ${Math.round(confidence * 100)}%`);
      lines.push('');
    }

    const refs = thesis.evidence_refs as string[] | undefined;
    if (refs && refs.length > 0) {
      lines.push(`**引用证据**: ${refs.join(', ')}`);
      lines.push('');
    }
  }

  // 支撑点
  if (supportPoints && supportPoints.length > 0) {
    lines.push('## 支撑点');
    lines.push('');
    supportPoints.forEach((point, i) => {
      const strength = point.strength as string;
      const strengthLabel = strength === 'strong' ? '强' : strength === 'medium' ? '中' : '弱';
      lines.push(`### ${i + 1}. ${point.content as string}`);
      lines.push(`- 强度: ${strengthLabel}`);
      if (point.evidence_id) {
        lines.push(`- 证据: ${point.evidence_id as string}`);
      }
      lines.push('');
    });
  }

  // 置信度说明
  if (confidenceNotes) {
    lines.push('## 置信度说明');
    lines.push('');

    const limitations = confidenceNotes.limitations as string[] | undefined;
    if (limitations && limitations.length > 0) {
      lines.push('### 局限性');
      for (const lim of limitations) {
        lines.push(`- ${lim}`);
      }
      lines.push('');
    }

    const assumptions = confidenceNotes.assumptions as string[] | undefined;
    if (assumptions && assumptions.length > 0) {
      lines.push('### 假设条件');
      for (const asm of assumptions) {
        lines.push(`- ${asm}`);
      }
      lines.push('');
    }
  }

  return lines;
}

function convertSemanticReviewToMarkdown(data: Record<string, unknown>): string[] {
  const lines: string[] = [];

  lines.push('## 审核结果');
  lines.push('');
  lines.push(data.passed ? '**✅ 通过**' : '**❌ 未通过**');
  lines.push('');

  const severitySummary = data.severity_summary as Record<string, number> | undefined;
  if (severitySummary) {
    lines.push('### 问题统计');
    lines.push(`- 低: ${severitySummary.low || 0}`);
    lines.push(`- 中: ${severitySummary.medium || 0}`);
    lines.push(`- 高: ${severitySummary.high || 0}`);
    lines.push(`- 严重: ${severitySummary.critical || 0}`);
    lines.push('');
  }

  const findings = data.findings as Array<Record<string, unknown>> | undefined;
  if (findings && findings.length > 0) {
    lines.push('### 发现问题');
    lines.push('');
    findings.forEach((finding, i) => {
      lines.push(`#### 问题 ${i + 1}`);
      lines.push(`- **严重程度**: ${finding.severity as string}`);
      lines.push(`- **类别**: ${finding.category as string}`);
      lines.push(`- **描述**: ${finding.description as string}`);
      if (finding.suggestion) {
        lines.push(`- **建议**: ${finding.suggestion as string}`);
      }
      lines.push('');
    });
  }

  return lines;
}

function convertWorkflowToMarkdown(data: Record<string, unknown>): string[] {
  const lines: string[] = [];

  lines.push('## 工作流状态');
  lines.push('');
  lines.push(`**状态**: ${data.status as string}`);
  lines.push('');

  const childResults = data.child_results as Array<Record<string, unknown>> | undefined;
  if (childResults && childResults.length > 0) {
    lines.push('### 子任务');
    lines.push('');
    childResults.forEach((child, i) => {
      lines.push(`${i + 1}. **${child.module_name as string}** - ${child.status as string}`);
      if (child.error) {
        lines.push(`   - 错误: ${child.error as string}`);
      }
    });
    lines.push('');
  }

  const errors = data.errors as string[] | undefined;
  if (errors && errors.length > 0) {
    lines.push('### 错误');
    for (const e of errors) {
      lines.push(`- ${e}`);
    }
    lines.push('');
  }

  return lines;
}