/**
 * Standard Chain Config Form
 *
 * SP-7D: 标准六段链配置表单 - Evidence → Planning → Writing → Drafting → Quality → Delivery
 *
 * 术语说明:
 * - Writing (写作): 编译生成 system_prompt 和 user_prompt
 * - Drafting (成稿): 将 prompts 转换为正文内容
 * - Quality (质量): 审核 Drafting 的正文内容
 * - Delivery (交付): 接收 Drafting 的正文内容
 */

import { useState, useCallback } from 'react';
import { Card, CardHeader, CardBody, Button, Badge } from '../ui';
import { EvidenceQueryPanel } from '../EvidenceQueryPanel';
import { PlanningConfigForm } from '../PlanningConfigForm';
import { WritingProgressView } from '../WritingProgressView';
import { DraftingPanel } from '../DraftingPanel';
import { QualityReportView } from '../QualityReportView';
import { DeliveryPanel } from '../DeliveryPanel';
import { compileDraft, reviewQuality, ApiError } from '../../api';
import type { FactRecord, PlanningResponse, CompiledPromptResponse, DraftingResult, QualityResult } from '../../types';

interface StandardChainConfigFormProps {
  disabled?: boolean;
}

type ChainStep = 'evidence' | 'planning' | 'writing' | 'drafting' | 'quality' | 'delivery';

export function StandardChainConfigForm({ disabled = false }: StandardChainConfigFormProps) {
  const [currentStep, setCurrentStep] = useState<ChainStep>('evidence');
  const [selectedFacts, setSelectedFacts] = useState<FactRecord[]>([]);
  const [plan, setPlan] = useState<PlanningResponse | null>(null);
  const [writingResult, setWritingResult] = useState<CompiledPromptResponse | null>(null);
  const [draftingResult, setDraftingResult] = useState<DraftingResult | null>(null);
  const [qualityResult, setQualityResult] = useState<QualityResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFactsSelected = useCallback((facts: FactRecord[]) => {
    setSelectedFacts(facts);
    setPlan(null);
    setWritingResult(null);
    setDraftingResult(null);
    setQualityResult(null);
    setError(null);
    if (facts.length > 0) {
      setCurrentStep('planning');
    }
  }, []);

  const handlePlanGenerated = useCallback((newPlan: PlanningResponse) => {
    setPlan(newPlan);
    setWritingResult(null);
    setDraftingResult(null);
    setQualityResult(null);
    setError(null);
    setCurrentStep('writing');
  }, []);

  const handleWritingComplete = useCallback(async () => {
    if (!plan) return;

    setLoading(true);
    setError(null);
    setDraftingResult(null);
    setQualityResult(null);

    try {
      const result = await compileDraft({
        thesis: plan.thesis || '',
        outline: plan.outline.map((item) => ({
          title: item.title,
          type: item.type,
          domain: item.domain,
        })),
        play_id: plan.play_id,
        arc_id: plan.arc_id,
        target_audience: plan.target_audience,
        key_evidence: plan.key_evidence,
      });

      setWritingResult(result);
      setCurrentStep('drafting');
    } catch (e) {
      const message = e instanceof ApiError ? e.message : '写作编译失败';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [plan]);

  const handleDraftingComplete = useCallback(async (result: DraftingResult) => {
    setLoading(true);
    setError(null);
    setDraftingResult(result);
    setQualityResult(null);

    try {
      // 自动触发质量审核 - 使用 Drafting 的正文内容
      const quality = await reviewQuality({ content: result.content });
      setQualityResult(quality);
      setCurrentStep('quality');
    } catch (e) {
      const message = e instanceof ApiError ? e.message : '质量审核失败';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const getStepStatus = (step: ChainStep): 'completed' | 'current' | 'pending' => {
    const steps: ChainStep[] = ['evidence', 'planning', 'writing', 'drafting', 'quality', 'delivery'];
    const currentIndex = steps.indexOf(currentStep);
    const stepIndex = steps.indexOf(step);

    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'current';
    return 'pending';
  };

  const getStepBadge = (step: ChainStep) => {
    const status = getStepStatus(step);
    switch (status) {
      case 'completed':
        return <Badge variant="success">已完成</Badge>;
      case 'current':
        return <Badge variant="info">进行中</Badge>;
      default:
        return <Badge variant="default">待执行</Badge>;
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900">标准六段链</h3>
          <Badge variant="info">一期</Badge>
        </div>
      </CardHeader>
      <CardBody className="space-y-4">
        {/* 进度指示器 - 六步 */}
        <div className="flex items-center justify-between text-xs">
          <button
            type="button"
            onClick={() => setCurrentStep('evidence')}
            className="flex items-center gap-1"
            disabled={disabled}
          >
            <span className={currentStep === 'evidence' ? 'text-blue-600 font-medium' : 'text-gray-500'}>
              证据
            </span>
            {getStepBadge('evidence')}
          </button>
          <span className="text-gray-300">→</span>
          <button
            type="button"
            onClick={() => selectedFacts.length > 0 && setCurrentStep('planning')}
            className="flex items-center gap-1"
            disabled={disabled || selectedFacts.length === 0}
          >
            <span className={currentStep === 'planning' ? 'text-blue-600 font-medium' : 'text-gray-500'}>
              规划
            </span>
            {getStepBadge('planning')}
          </button>
          <span className="text-gray-300">→</span>
          <button
            type="button"
            onClick={() => plan && setCurrentStep('writing')}
            className="flex items-center gap-1"
            disabled={disabled || !plan}
          >
            <span className={currentStep === 'writing' ? 'text-blue-600 font-medium' : 'text-gray-500'}>
              写作
            </span>
            {getStepBadge('writing')}
          </button>
          <span className="text-gray-300">→</span>
          <button
            type="button"
            onClick={() => writingResult && setCurrentStep('drafting')}
            className="flex items-center gap-1"
            disabled={disabled || !writingResult}
          >
            <span className={currentStep === 'drafting' ? 'text-blue-600 font-medium' : 'text-gray-500'}>
              成稿
            </span>
            {getStepBadge('drafting')}
          </button>
          <span className="text-gray-300">→</span>
          <button
            type="button"
            onClick={() => draftingResult && setCurrentStep('quality')}
            className="flex items-center gap-1"
            disabled={disabled || !draftingResult}
          >
            <span className={currentStep === 'quality' ? 'text-blue-600 font-medium' : 'text-gray-500'}>
              质量
            </span>
            {getStepBadge('quality')}
          </button>
          <span className="text-gray-300">→</span>
          <button
            type="button"
            onClick={() => qualityResult && setCurrentStep('delivery')}
            className="flex items-center gap-1"
            disabled={disabled || !qualityResult}
          >
            <span className={currentStep === 'delivery' ? 'text-blue-600 font-medium' : 'text-gray-500'}>
              交付
            </span>
            {getStepBadge('delivery')}
          </button>
        </div>

        {/* 错误信息 */}
        {error && (
          <div className="p-2 bg-red-50 border border-red-200 rounded">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* 当前步骤内容 */}
        {currentStep === 'evidence' && (
          <EvidenceQueryPanel
            onFactsSelected={handleFactsSelected}
            disabled={disabled || loading}
          />
        )}

        {currentStep === 'planning' && (
          <PlanningConfigForm
            selectedFacts={selectedFacts}
            onPlanGenerated={handlePlanGenerated}
            disabled={disabled || loading}
          />
        )}

        {currentStep === 'writing' && (
          <>
            <WritingProgressView
              result={writingResult || undefined}
              plan={plan || undefined}
              onWriteComplete={handleWritingComplete}
            />
            {loading && (
              <div className="mt-2 text-center text-sm text-gray-500">
                正在编译写作指令...
              </div>
            )}
          </>
        )}

        {currentStep === 'drafting' && (
          <>
            <DraftingPanel
              writingResult={writingResult || undefined}
              onDraftingComplete={handleDraftingComplete}
              disabled={disabled || loading}
            />
            {loading && (
              <div className="mt-2 text-center text-sm text-gray-500">
                正在生成正文并触发质量审核...
              </div>
            )}
          </>
        )}

        {currentStep === 'quality' && (
          <>
            <QualityReportView
              result={qualityResult || undefined}
              content={draftingResult?.content}
            />
            {qualityResult?.overall_status === 'passed' && (
              <Button
                onClick={() => setCurrentStep('delivery')}
                className="w-full mt-2"
              >
                继续交付
              </Button>
            )}
          </>
        )}

        {currentStep === 'delivery' && (
          <DeliveryPanel
            plan={plan || undefined}
            qualityResult={qualityResult || undefined}
            content={draftingResult?.content}
            disabled={disabled || loading}
          />
        )}
      </CardBody>
    </Card>
  );
}
