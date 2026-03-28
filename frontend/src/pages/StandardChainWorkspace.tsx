/**
 * Standard Chain Workspace — 标准六段链工作区（三栏布局）
 * 
 * 左侧步骤导航 + 中间工作区 + 右侧摘要
 */

import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody, Button, Badge, Spinner } from '../components/ui';
import { EvidenceQueryPanel } from '../components/EvidenceQueryPanel';
import { PlanningConfigForm } from '../components/PlanningConfigForm';
import { WritingProgressView } from '../components/WritingProgressView';
import { DraftingPanel } from '../components/DraftingPanel';
import { QualityReportView } from '../components/QualityReportView';
import { DeliveryPanel } from '../components/DeliveryPanel';
import { compileDraft, reviewQuality, ApiError } from '../api';
import type { FactRecord, PlanningResponse, CompiledPromptResponse, DraftingResult, QualityResult } from '../types';

type ChainStep = 'evidence' | 'planning' | 'writing' | 'drafting' | 'quality' | 'delivery';

const STEPS: { id: ChainStep; label: string; number: number }[] = [
  { id: 'evidence', label: '证据查询', number: 1 },
  { id: 'planning', label: '规划生成', number: 2 },
  { id: 'writing', label: '写作编译', number: 3 },
  { id: 'drafting', label: '成稿生成', number: 4 },
  { id: 'quality', label: '质量审核', number: 5 },
  { id: 'delivery', label: '交付', number: 6 },
];

export function StandardChainWorkspace() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<ChainStep>('evidence');
  const [selectedFacts, setSelectedFacts] = useState<FactRecord[]>([]);
  const [plan, setPlan] = useState<PlanningResponse | null>(null);
  const [writingResult, setWritingResult] = useState<CompiledPromptResponse | null>(null);
  const [draftingResult, setDraftingResult] = useState<DraftingResult | null>(null);
  const [qualityResult, setQualityResult] = useState<QualityResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 读取从新建页传入的初始化参数
  const [initParams] = useState(() => {
    try {
      const raw = sessionStorage.getItem('xiakedao_chain_init');
      if (raw) {
        sessionStorage.removeItem('xiakedao_chain_init');
        return JSON.parse(raw);
      }
    } catch {}
    return null;
  });

  const handleFactsSelected = useCallback((facts: FactRecord[]) => {
    setSelectedFacts(facts);
    setPlan(null);
    setWritingResult(null);
    setDraftingResult(null);
    setQualityResult(null);
    setError(null);
    if (facts.length > 0) setCurrentStep('planning');
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
    try {
      const result = await compileDraft({
        thesis: plan.thesis || '',
        outline: plan.outline.map(item => ({
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
      setError(e instanceof ApiError ? e.message : '写作编译失败');
    } finally {
      setLoading(false);
    }
  }, [plan]);

  const handleDraftingComplete = useCallback(async (result: DraftingResult) => {
    setLoading(true);
    setError(null);
    setDraftingResult(result);
    try {
      const quality = await reviewQuality({ content: result.content });
      setQualityResult(quality);
      setCurrentStep('quality');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : '质量审核失败');
    } finally {
      setLoading(false);
    }
  }, []);

  const getStepStatus = (step: ChainStep): 'completed' | 'current' | 'pending' | 'error' => {
    const steps: ChainStep[] = ['evidence', 'planning', 'writing', 'drafting', 'quality', 'delivery'];
    const currentIndex = steps.indexOf(currentStep);
    const stepIndex = steps.indexOf(step);
    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'current';
    return 'pending';
  };

  const canNavigateTo = (step: ChainStep): boolean => {
    switch (step) {
      case 'evidence': return true;
      case 'planning': return selectedFacts.length > 0;
      case 'writing': return !!plan;
      case 'drafting': return !!writingResult;
      case 'quality': return !!draftingResult;
      case 'delivery': return !!qualityResult;
    }
  };

  return (
    <div className="max-w-[1600px] mx-auto px-4 py-6 h-[calc(100vh-64px)] flex flex-col animate-in fade-in duration-300">
      <div className="flex items-center justify-between mb-6 shrink-0">
        <div>
           <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
             <span className="w-2 h-6 bg-brand-500 rounded-sm"></span>
             标准六段链控制台
           </h2>
           <p className="text-xs text-slate-500 mt-1 ml-4">The Standard 6-Step Chain Workspace</p>
        </div>
        <Button variant="ghost" size="sm" onClick={() => navigate('/')} className="text-slate-500 hover:text-slate-900">
          退出控制台
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 flex-1 min-h-0">
        {/* 左侧 - 步骤导航 */}
        <div className="md:col-span-3 xl:col-span-2 flex flex-col shrink-0 overflow-y-auto pr-1">
          <Card className="flex-1 bg-slate-50/50 border-slate-200/60 shadow-none">
            <div className="px-4 py-3 border-b border-slate-100/60 font-semibold text-xs text-slate-500 uppercase tracking-wider">
               流水线进度 (Pipeline)
            </div>
            <CardBody className="p-3 space-y-1.5">
              {STEPS.map((step, index) => {
                const status = getStepStatus(step.id);
                const canNav = canNavigateTo(step.id);
                const isLast = index === STEPS.length - 1;
                return (
                  <div key={step.id} className="relative">
                    {/* 连接线 */}
                    {!isLast && (
                       <div className={`absolute left-4 top-8 bottom-[-10px] w-px ${status === 'completed' ? 'bg-brand-300' : 'bg-slate-200'}`}></div>
                    )}
                    <button
                      type="button"
                      onClick={() => canNav && setCurrentStep(step.id)}
                      disabled={!canNav}
                      className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-all duration-200 flex items-center gap-3 ${
                        status === 'current'
                          ? 'bg-white text-brand-700 font-semibold shadow-sm border border-brand-100 outline outline-2 outline-offset-1 outline-brand-500/20 z-10 relative'
                          : status === 'completed'
                          ? 'text-slate-700 hover:bg-white z-10 relative'
                          : 'text-slate-400 cursor-not-allowed opacity-60 z-10 relative'
                      }`}
                    >
                      <span className={`w-6 h-6 shrink-0 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${
                        status === 'current'
                          ? 'bg-brand-600 text-white shadow-md shadow-brand-500/30'
                          : status === 'completed'
                          ? 'bg-brand-100 text-brand-600 border border-brand-200'
                          : 'bg-slate-100 text-slate-400 border border-slate-200'
                      }`}>
                        {status === 'completed' ? '✓' : step.number}
                      </span>
                      <span>{step.label}</span>
                    </button>
                  </div>
                );
              })}
            </CardBody>
          </Card>
        </div>

        {/* 中间 - 工作区 */}
        <div className="md:col-span-9 xl:col-span-7 flex flex-col min-h-0 overflow-y-auto bg-white rounded-xl border border-slate-200/60 shadow-sm p-6 relative">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
              <Button variant="ghost" size="sm" className="mt-1" onClick={() => setError(null)}>
                关闭
              </Button>
            </div>
          )}

          {currentStep === 'evidence' && (
            <EvidenceQueryPanel
              onFactsSelected={handleFactsSelected}
              disabled={loading}
            />
          )}

          {currentStep === 'planning' && (
            <PlanningConfigForm
              selectedFacts={selectedFacts}
              onPlanGenerated={handlePlanGenerated}
              disabled={loading}
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
                <div className="mt-4 text-center">
                  <Spinner size="md" />
                  <p className="text-sm text-gray-500 mt-2">正在编译写作指令...</p>
                </div>
              )}
            </>
          )}

          {currentStep === 'drafting' && (
            <>
              <DraftingPanel
                writingResult={writingResult || undefined}
                onDraftingComplete={handleDraftingComplete}
                disabled={loading}
              />
              {loading && (
                <div className="mt-4 text-center">
                  <Spinner size="md" />
                  <p className="text-sm text-gray-500 mt-2">正在生成正文并触发质量审核...</p>
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
              <div className="mt-4 flex gap-2">
                {qualityResult?.overall_status === 'passed' && (
                  <Button onClick={() => setCurrentStep('delivery')}>
                    继续交付
                  </Button>
                )}
                <Button
                  variant="secondary"
                  onClick={() => setCurrentStep('drafting')}
                >
                  回退到成稿
                </Button>
              </div>
            </>
          )}

          {currentStep === 'delivery' && (
            <DeliveryPanel
              plan={plan || undefined}
              qualityResult={qualityResult || undefined}
              content={draftingResult?.content}
              disabled={loading}
            />
          )}
        </div>

        {/* 右侧 - 摘要栏 */}
        <div className="hidden xl:flex xl:col-span-3 flex-col shrink-0 space-y-4 overflow-y-auto pr-1">
          {/* 任务进度概览 */}
          <Card className="bg-slate-50/50 shadow-none border-slate-200/60">
            <CardHeader className="py-2.5 bg-slate-100/50">
              <h3 className="text-xs font-bold text-slate-600 uppercase tracking-wider">任务状态摘要</h3>
            </CardHeader>
            <CardBody className="space-y-3 text-sm">
              {initParams && (
                <div>
                  <span className="text-gray-500">产品：</span>
                  <span className="font-medium">{initParams.productId || '—'}</span>
                </div>
              )}
              <div>
                <span className="text-gray-500">已选证据：</span>
                <span className="font-medium">{selectedFacts.length} 条</span>
              </div>
              {plan && (
                <>
                  <div>
                    <span className="text-gray-500">核心论点：</span>
                    <p className="text-xs text-gray-700 mt-0.5">
                      {plan.thesis ? plan.thesis.slice(0, 80) + (plan.thesis.length > 80 ? '...' : '') : '—'}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">大纲段落：</span>
                    <span className="font-medium">{plan.outline.length} 段</span>
                  </div>
                </>
              )}
              {draftingResult && (
                <div>
                  <span className="text-gray-500">正文字数：</span>
                  <span className="font-medium">{draftingResult.word_count}</span>
                </div>
              )}
              {qualityResult && (
                <div>
                  <span className="text-gray-500">质量审核：</span>
                  <Badge
                    variant={qualityResult.overall_status === 'passed' ? 'success' : 'danger'}
                    size="sm"
                  >
                    {qualityResult.overall_status === 'passed' ? '通过' : '未通过'}
                  </Badge>
                </div>
              )}
            </CardBody>
          </Card>

          {/* 已选事实列表 */}
          {selectedFacts.length > 0 && (
            <Card className="shadow-sm">
              <CardHeader className="py-2.5 bg-slate-50/50 border-b-slate-100">
                <h3 className="text-xs font-bold text-slate-700 flex justify-between items-center w-full">
                  <span>已锁定事实网络</span>
                  <Badge variant="info" size="sm">{selectedFacts.length}</Badge>
                </h3>
              </CardHeader>
              <CardBody className="p-0 max-h-60 overflow-y-auto">
                <div className="divide-y divide-gray-100">
                  {selectedFacts.map(fact => (
                    <div key={fact.fact_id} className="px-3 py-2">
                      <div className="flex items-center gap-1">
                        <Badge variant="info" size="sm">{fact.domain}</Badge>
                        <span className="text-xs text-gray-500 font-mono">{fact.fact_key}</span>
                      </div>
                      <p className="text-xs text-gray-700 mt-0.5 line-clamp-2">{fact.value}</p>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          )}

          {/* 大纲预览 */}
          {plan && plan.outline.length > 0 && (
            <Card className="shadow-sm">
              <CardHeader className="py-2.5 bg-slate-50/50 border-b-slate-100">
                <h3 className="text-xs font-bold text-slate-700 w-full">生成大纲框架</h3>
              </CardHeader>
              <CardBody className="p-0 max-h-48 overflow-y-auto">
                <div className="divide-y divide-gray-100">
                  {plan.outline.map((item, i) => (
                    <div key={i} className="px-3 py-2 text-xs text-gray-700">
                      <span className="font-medium">{i + 1}. {item.title}</span>
                      {item.domain && (
                        <Badge variant="default" size="sm" className="ml-1">{item.domain}</Badge>
                      )}
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          )}

          {/* 产物预览 */}
          {draftingResult && (
            <Card className="shadow-sm">
              <CardHeader className="py-2.5 bg-slate-50/50 border-b-slate-100">
                <h3 className="text-xs font-bold text-slate-700 w-full">Draft Preview</h3>
              </CardHeader>
              <CardBody>
                <div className="max-h-40 overflow-y-auto text-xs text-gray-700 whitespace-pre-wrap">
                  {draftingResult.content.slice(0, 500)}
                  {draftingResult.content.length > 500 && '...'}
                </div>
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
