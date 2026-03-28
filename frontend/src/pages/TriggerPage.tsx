/**
 * Trigger Page
 * 
 * 一期前端触发设置页 - 单页统一入口
 */

import { useState, useCallback } from 'react';
import { Card, CardHeader, CardBody, Button, Tabs, TabsList, TabsTrigger, Badge } from '../components/ui';
import { useDraftStorage } from '../hooks';
import { 
  TRIGGER_TARGETS, 
  type TargetId, 
  type OpinionDraftConfig,
  type SemanticReviewDraftConfig,
  type ArticleDraftConfig,
  type StandardChainDraftConfig,
  type OpinionGenerateRequest,
  type SemanticReviewRequest,
  type ArticleWorkflowRequest,
  type OpinionGenerateResponse,
  type SemanticReviewResponse,
  type ArticleWorkflowResponse,
  type TaskSummary,
  transformOpinionResponse,
  transformSemanticReviewResponse,
  transformArticleWorkflowResponse,
  createTaskSummary,
} from '../types';
import { generateOpinion, reviewSemantic, executeArticleWorkflow, ApiError } from '../api';
import { OpinionConfigForm, SemanticReviewConfigForm, ArticleWorkflowConfigForm, StandardChainConfigForm } from '../components/forms';
import { OpinionResultView } from '../components/results/OpinionResultView';
import { SemanticReviewResultView } from '../components/results/SemanticReviewResultView';
import { ArticleWorkflowResultView } from '../components/results/ArticleWorkflowResultView';
import { RunStatusBanner } from '../components/RunStatusBanner';
import { RecentRunList } from '../components/RecentRunList';
import { HistoryPanel } from '../components/HistoryPanel';

type RunStatus = 'idle' | 'running' | 'success' | 'error';

interface ExecutionState {
  status: RunStatus;
  error?: string;
  opinionResult?: OpinionGenerateResponse;
  semanticReviewResult?: SemanticReviewResponse;
  articleResult?: ArticleWorkflowResponse;
}

export function TriggerPage() {
  // 当前选中的目标
  const [activeTarget, setActiveTarget] = useState<TargetId>('opinion');
  
  // 各目标的草稿
  const opinionDraft = useDraftStorage<OpinionDraftConfig>('opinion');
  const semanticReviewDraft = useDraftStorage<SemanticReviewDraftConfig>('semantic_review');
  const articleDraft = useDraftStorage<ArticleDraftConfig>('article');
  const standardChainDraft = useDraftStorage<StandardChainDraftConfig>('standard_chain');
  
  // 执行状态
  const [execution, setExecution] = useState<ExecutionState>({ status: 'idle' });
  
  // 最近执行列表
  const [recentRuns, setRecentRuns] = useState<TaskSummary[]>([]);
  
  // 基于历史任务的标记
  const [basedOnTaskId, setBasedOnTaskId] = useState<string | null>(null);
  
  // 执行 Opinion
  const handleOpinionSubmit = useCallback(async (request: OpinionGenerateRequest) => {
    setExecution({ status: 'running' });
    const launchedAt = new Date().toISOString();
    
    try {
      const result = await generateOpinion(request);
      setExecution({ status: 'success', opinionResult: result });
      
      // 添加到最近执行
      const runResult = transformOpinionResponse(result, launchedAt);
      const summary = createTaskSummary(runResult, '观点生成');
      setRecentRuns(prev => [summary, ...prev].slice(0, 5));
      
      // 清除基于历史任务的标记
      setBasedOnTaskId(null);
    } catch (e) {
      const message = e instanceof ApiError ? e.message : '未知错误';
      setExecution({ status: 'error', error: message });
    }
  }, []);
  
  // 执行 Semantic Review
  const handleSemanticReviewSubmit = useCallback(async (request: SemanticReviewRequest) => {
    setExecution({ status: 'running' });
    const launchedAt = new Date().toISOString();
    
    try {
      const result = await reviewSemantic(request);
      setExecution({ status: 'success', semanticReviewResult: result });
      
      const runResult = transformSemanticReviewResponse(result, launchedAt);
      const summary = createTaskSummary(runResult, '语义审核');
      setRecentRuns(prev => [summary, ...prev].slice(0, 5));
      
      setBasedOnTaskId(null);
    } catch (e) {
      const message = e instanceof ApiError ? e.message : '未知错误';
      setExecution({ status: 'error', error: message });
    }
  }, []);
  
  // 执行 Article Workflow
  const handleArticleSubmit = useCallback(async (request: ArticleWorkflowRequest) => {
    setExecution({ status: 'running' });
    const launchedAt = new Date().toISOString();
    
    try {
      const result = await executeArticleWorkflow(request);
      setExecution({ status: 'success', articleResult: result });
      
      const runResult = transformArticleWorkflowResponse(result, launchedAt);
      const summary = createTaskSummary(runResult, '文章工作流');
      setRecentRuns(prev => [summary, ...prev].slice(0, 5));
      
      setBasedOnTaskId(null);
    } catch (e) {
      const message = e instanceof ApiError ? e.message : '未知错误';
      setExecution({ status: 'error', error: message });
    }
  }, []);
  
  // 切换目标时重置执行状态
  const handleTargetChange = useCallback((target: string) => {
    setActiveTarget(target as TargetId);
    setExecution({ status: 'idle' });
  }, []);
  
  // 从历史任务加载参数
  const handleLoadParams = useCallback((module: string, params: Record<string, unknown>, sourceTaskId?: string) => {
    // 检查当前草稿是否已被修改
    const currentDraftDirty = 
      (module === 'opinion' && opinionDraft.isDirty) ||
      (module === 'semantic_review' && semanticReviewDraft.isDirty) ||
      (module === 'orchestrator' && articleDraft.isDirty) ||
      (module === 'standard_chain' && standardChainDraft.isDirty);
    
    // 如果草稿已被修改，提示用户确认
    if (currentDraftDirty) {
      const confirmed = window.confirm('当前草稿已被修改，加载历史参数将覆盖现有修改。是否继续？');
      if (!confirmed) {
        return;
      }
    }
    
    // 切换到对应的目标
    if (module === 'opinion') {
      setActiveTarget('opinion');
      opinionDraft.saveDraft(params as unknown as OpinionDraftConfig);
    } else if (module === 'semantic_review') {
      setActiveTarget('semantic_review');
      semanticReviewDraft.saveDraft(params as unknown as SemanticReviewDraftConfig);
    } else if (module === 'orchestrator') {
      setActiveTarget('article');
      // 工作流参数需要特殊处理
      articleDraft.saveDraft(params as unknown as ArticleDraftConfig);
    }
    
    // 设置基于历史任务的标记
    if (sourceTaskId) {
      setBasedOnTaskId(sourceTaskId);
    }
    
    setExecution({ status: 'idle' });
  }, [opinionDraft, semanticReviewDraft, articleDraft, standardChainDraft]);
  
  // 处理复制任务
  const handleCopy = useCallback((_newTaskId: string, originalTaskId: string) => {
    // 设置基于历史任务的标记
    setBasedOnTaskId(originalTaskId);
    // 清除执行状态
    setExecution({ status: 'idle' });
  }, []);
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 头部 */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900">侠客岛 - 触发设置</h1>
              <p className="text-sm text-gray-500">一期前端触发设置页 - 执行入口</p>
            </div>
            <Badge variant="info">一期</Badge>
          </div>
        </div>
      </header>
      
      {/* 主内容 */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧：表单区域 */}
          <div className="lg:col-span-2 space-y-4">
            {/* 目标选择器 */}
            <Card>
              <CardBody className="py-3">
                <Tabs defaultValue={activeTarget} onChange={handleTargetChange}>
                  <TabsList>
                    {TRIGGER_TARGETS.map(target => (
                      <TabsTrigger key={target.id} value={target.id}>
                        {target.label}
                        {target.phaseTag === '一期' && (
                          <Badge variant="success" size="sm" className="ml-2">一期</Badge>
                        )}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                </Tabs>
              </CardBody>
            </Card>
            
            {/* 草稿操作栏 */}
            <Card>
              <CardBody className="py-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500">本地草稿</span>
                  {(activeTarget === 'opinion' && opinionDraft.isDirty && (
                    <Badge variant="warning" size="sm">已修改</Badge>
                  )) || (activeTarget === 'semantic_review' && semanticReviewDraft.isDirty && (
                    <Badge variant="warning" size="sm">已修改</Badge>
                  )) || (activeTarget === 'article' && articleDraft.isDirty && (
                    <Badge variant="warning" size="sm">已修改</Badge>
                  )) || (activeTarget === 'standard_chain' && standardChainDraft.isDirty && (
                    <Badge variant="warning" size="sm">已修改</Badge>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      if (activeTarget === 'opinion') opinionDraft.resetToDefault();
                      else if (activeTarget === 'semantic_review') semanticReviewDraft.resetToDefault();
                      else if (activeTarget === 'article') articleDraft.resetToDefault();
                      else if (activeTarget === 'standard_chain') standardChainDraft.resetToDefault();
                    }}
                  >
                    恢复默认
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      if (activeTarget === 'opinion') opinionDraft.clearDraft();
                      else if (activeTarget === 'semantic_review') semanticReviewDraft.clearDraft();
                      else if (activeTarget === 'article') articleDraft.clearDraft();
                      else if (activeTarget === 'standard_chain') standardChainDraft.clearDraft();
                    }}
                  >
                    清空草稿
                  </Button>
                </div>
              </CardBody>
            </Card>
            
            {/* 表单内容 */}
            <div className="min-h-[400px]">
              {activeTarget === 'opinion' && (
                <OpinionConfigForm
                  value={opinionDraft.draft}
                  onChange={opinionDraft.saveDraft}
                  onSubmit={handleOpinionSubmit}
                  disabled={execution.status === 'running'}
                />
              )}
              {activeTarget === 'semantic_review' && (
                <SemanticReviewConfigForm
                  value={semanticReviewDraft.draft}
                  onChange={semanticReviewDraft.saveDraft}
                  onSubmit={handleSemanticReviewSubmit}
                  disabled={execution.status === 'running'}
                />
              )}
              {activeTarget === 'article' && (
                <ArticleWorkflowConfigForm
                  value={articleDraft.draft}
                  onChange={articleDraft.saveDraft}
                  onSubmit={handleArticleSubmit}
                  disabled={execution.status === 'running'}
                />
              )}
              {activeTarget === 'standard_chain' && (
                <StandardChainConfigForm
                  disabled={execution.status === 'running'}
                />
              )}
            </div>
          </div>
          
          {/* 右侧：结果和最近执行 */}
          <div className="space-y-4">
            {/* 执行状态 */}
            <Card>
              <CardHeader>
                <h3 className="text-sm font-medium text-gray-900">执行状态</h3>
              </CardHeader>
              <CardBody>
                <RunStatusBanner 
                  status={execution.status} 
                  message={execution.status === 'running' ? '正在处理中...' : undefined}
                />
                {execution.error && (
                  <p className="mt-2 text-sm text-red-600">{execution.error}</p>
                )}
                {basedOnTaskId && execution.status === 'idle' && (
                  <p className="mt-2 text-sm text-blue-600">
                    参数已从历史任务 {basedOnTaskId.slice(0, 8)}... 加载
                  </p>
                )}
              </CardBody>
            </Card>
            
            {/* 结果展示 */}
            {execution.status === 'success' && (
              <Card>
                <CardHeader>
                  <h3 className="text-sm font-medium text-gray-900">执行结果</h3>
                </CardHeader>
                <CardBody className="max-h-[400px] overflow-y-auto">
                  {activeTarget === 'opinion' && execution.opinionResult && (
                    <OpinionResultView result={execution.opinionResult} />
                  )}
                  {activeTarget === 'semantic_review' && execution.semanticReviewResult && (
                    <SemanticReviewResultView result={execution.semanticReviewResult} />
                  )}
                  {activeTarget === 'article' && execution.articleResult && (
                    <ArticleWorkflowResultView result={execution.articleResult} />
                  )}
                </CardBody>
              </Card>
            )}
            
            {/* 最近执行 */}
            <RecentRunList runs={recentRuns} />
            
            {/* 任务历史面板 */}
            <HistoryPanel onLoadParams={handleLoadParams} onCopy={handleCopy} maxHeight="300px" />
          </div>
        </div>
      </main>
      
      {/* 底部说明 */}
      <footer className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <p className="text-xs text-gray-500 text-center">
            本次仅完成一期前端原型，不包含二三期自动化平台能力。草稿仅保存在浏览器本地，不跨设备同步。
          </p>
        </div>
      </footer>
    </div>
  );
}