/**
 * Planning Config Form
 * 
 * 规划配置表单 - 用于配置和生成编辑计划
 */

import { useState, useCallback } from 'react';
import { Card, CardHeader, CardBody, Button, Input, Select, Badge } from './ui';
import { generatePlan, ApiError } from '../api';
import type { PlanningResponse, FactRecord, RouteContextRequest } from '../types';

interface PlanningConfigFormProps {
  selectedFacts?: FactRecord[];
  onPlanGenerated?: (plan: PlanningResponse) => void;
  disabled?: boolean;
}

const REGISTER_OPTIONS = [
  { value: 'clinical', label: '临床注册' },
  { value: 'research', label: '科研注册' },
  { value: 'education', label: '教育注册' },
];

const DELIVERABLE_TYPE_OPTIONS = [
  { value: '', label: '默认' },
  { value: 'article', label: '文章' },
  { value: 'brief', label: '简报' },
  { value: 'report', label: '报告' },
];

export function PlanningConfigForm({
  selectedFacts = [],
  onPlanGenerated,
  disabled = false,
}: PlanningConfigFormProps) {
  const [context, setContext] = useState<RouteContextRequest>({
    product_id: '',
    register: 'clinical',
    audience: '医学专业人士',
    project_name: '',
    deliverable_type: '',
    metadata: {},
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [plan, setPlan] = useState<PlanningResponse | null>(null);

  const updateContext = (updates: Partial<RouteContextRequest>) => {
    setContext((prev) => ({ ...prev, ...updates }));
  };

  const handleSubmit = useCallback(async () => {
    if (!context.product_id) {
      setError('请输入产品 ID');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const evidenceFacts = selectedFacts.map((f) => ({
        fact_id: f.fact_id,
        domain: f.domain,
        fact_key: f.fact_key,
        value: f.value,
      }));

      const result = await generatePlan({
        context,
        evidence_facts: evidenceFacts.length > 0 ? evidenceFacts : undefined,
        selected_facts: selectedFacts.map((f) => f.fact_id),
      });

      setPlan(result);
      onPlanGenerated?.(result);
    } catch (e) {
      const message = e instanceof ApiError ? e.message : '规划生成失败';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [context, selectedFacts, onPlanGenerated]);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900">规划配置</h3>
          <Badge variant="info">一期</Badge>
        </div>
      </CardHeader>
      <CardBody className="space-y-4">
        {/* 基本信息 */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">产品 ID *</label>
            <Input
              value={context.product_id}
              onChange={(e) => updateContext({ product_id: e.target.value })}
              placeholder="例如: lecanemab"
              disabled={disabled || loading}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">项目名称</label>
            <Input
              value={context.project_name || ''}
              onChange={(e) => updateContext({ project_name: e.target.value })}
              placeholder="可选"
              disabled={disabled || loading}
            />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">注册</label>
            <Select
              value={context.register || 'clinical'}
              onChange={(e) => updateContext({ register: e.target.value })}
              disabled={disabled || loading}
              options={REGISTER_OPTIONS}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">受众</label>
            <Input
              value={context.audience}
              onChange={(e) => updateContext({ audience: e.target.value })}
              placeholder="目标受众"
              disabled={disabled || loading}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">交付类型</label>
            <Select
              value={context.deliverable_type || ''}
              onChange={(e) => updateContext({ deliverable_type: e.target.value })}
              disabled={disabled || loading}
              options={DELIVERABLE_TYPE_OPTIONS}
            />
          </div>
        </div>

        {/* 选中的证据 */}
        {selectedFacts.length > 0 && (
          <div className="p-2 bg-gray-50 rounded">
            <p className="text-xs text-gray-500 mb-1">已选择 {selectedFacts.length} 条证据</p>
            <div className="flex flex-wrap gap-1">
              {selectedFacts.slice(0, 5).map((f) => (
                <Badge key={f.fact_id} variant="default" size="sm">
                  {f.fact_key}
                </Badge>
              ))}
              {selectedFacts.length > 5 && (
                <Badge variant="default" size="sm">
                  +{selectedFacts.length - 5} 更多
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* 提交按钮 */}
        <div className="flex gap-2">
          <Button onClick={handleSubmit} disabled={disabled || loading}>
            生成规划
          </Button>
        </div>

        {/* 错误信息 */}
        {error && <p className="text-sm text-red-600">{error}</p>}

        {/* 规划结果 */}
        {plan && (
          <div className="border-t pt-4 space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium text-gray-900">规划结果</h4>
              <span className="text-xs text-gray-500">Task: {plan.task_id.slice(0, 8)}...</span>
            </div>

            {plan.thesis && (
              <div>
                <p className="text-xs text-gray-500 mb-1">核心论点</p>
                <p className="text-sm text-gray-900">{plan.thesis}</p>
              </div>
            )}

            {plan.outline.length > 0 && (
              <div>
                <p className="text-xs text-gray-500 mb-1">大纲</p>
                <ul className="space-y-1">
                  {plan.outline.map((item, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-sm">
                      <Badge variant="default" size="sm">
                        {item.type}
                      </Badge>
                      <span>{item.title}</span>
                      {item.fact_count && (
                        <span className="text-xs text-gray-400">({item.fact_count} 条证据)</span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="flex gap-4 text-xs text-gray-500">
              {plan.play_id && <span>策略: {plan.play_id}</span>}
              {plan.arc_id && <span>弧线: {plan.arc_id}</span>}
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  );
}