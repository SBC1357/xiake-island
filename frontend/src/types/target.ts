/**
 * Trigger Target Types
 * 
 * 触发目标的展示模型
 */

export type TargetId = 'opinion' | 'semantic_review' | 'article' | 'standard_chain';

export type TargetKind = 'module' | 'workflow';

export interface TriggerTargetView {
  id: TargetId;
  label: string;
  kind: TargetKind;
  description: string;
  submitEndpoint: string;
  enabled: boolean;
  phaseTag: '一期' | '即将开放';
}

// 预定义的四个目标
export const TRIGGER_TARGETS: TriggerTargetView[] = [
  {
    id: 'opinion',
    label: '观点生成',
    kind: 'module',
    description: '根据证据材料生成结构化医学观点',
    submitEndpoint: '/v1/opinion/generate',
    enabled: true,
    phaseTag: '一期',
  },
  {
    id: 'semantic_review',
    label: '语义审核',
    kind: 'module',
    description: '对中文内容进行语义审核，识别语法错误、表达不当等问题',
    submitEndpoint: '/v1/review/semantic',
    enabled: true,
    phaseTag: '一期',
  },
  {
    id: 'article',
    label: '文章工作流',
    kind: 'workflow',
    description: '执行观点生成 → 语义审核的完整工作流',
    submitEndpoint: '/v1/workflow/article',
    enabled: true,
    phaseTag: '一期',
  },
  {
    id: 'standard_chain',
    label: '标准六段链',
    kind: 'workflow',
    description: '证据查询 → 规划 → 写作 → 成稿 → 质量 → 交付的完整链路',
    submitEndpoint: '/v1/workflow/standard-chain',
    enabled: true,
    phaseTag: '一期',
  },
];

export function getTargetById(id: TargetId): TriggerTargetView | undefined {
  return TRIGGER_TARGETS.find(t => t.id === id);
}