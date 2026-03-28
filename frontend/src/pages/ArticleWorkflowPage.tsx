/**
 * Article Workflow Page — 文章工作流页
 * 
 * 保留现有 ArticleWorkflowConfigForm 和 ArticleWorkflowResultView，做样式统一
 */

import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody, Button } from '../components/ui';
import { useDraftStorage } from '../hooks';
import { ArticleWorkflowConfigForm } from '../components/forms';
import { ArticleWorkflowResultView } from '../components/results/ArticleWorkflowResultView';
import { OpinionConfigForm } from '../components/forms';
import { OpinionResultView } from '../components/results/OpinionResultView';
import { SemanticReviewConfigForm } from '../components/forms';
import { SemanticReviewResultView } from '../components/results/SemanticReviewResultView';
import { RunStatusBanner } from '../components/RunStatusBanner';
import { generateOpinion, reviewSemantic, executeArticleWorkflow, ApiError } from '../api';
import type {
  ArticleDraftConfig,
  OpinionDraftConfig,
  SemanticReviewDraftConfig,
  OpinionGenerateRequest,
  SemanticReviewRequest,
  ArticleWorkflowRequest,
  OpinionGenerateResponse,
  SemanticReviewResponse,
  ArticleWorkflowResponse,
} from '../types';

type ActiveTab = 'article' | 'opinion' | 'semantic_review';
type RunStatus = 'idle' | 'running' | 'success' | 'error';

export function ArticleWorkflowPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<ActiveTab>('article');
  const [status, setStatus] = useState<RunStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const [articleResult, setArticleResult] = useState<ArticleWorkflowResponse | null>(null);
  const [opinionResult, setOpinionResult] = useState<OpinionGenerateResponse | null>(null);
  const [reviewResult, setReviewResult] = useState<SemanticReviewResponse | null>(null);

  const articleDraft = useDraftStorage<ArticleDraftConfig>('article');
  const opinionDraft = useDraftStorage<OpinionDraftConfig>('opinion');
  const reviewDraft = useDraftStorage<SemanticReviewDraftConfig>('semantic_review');

  const handleArticleSubmit = useCallback(async (req: ArticleWorkflowRequest) => {
    setStatus('running');
    setError(null);
    try {
      const result = await executeArticleWorkflow(req);
      setArticleResult(result);
      setStatus('success');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : '工作流执行失败');
      setStatus('error');
    }
  }, []);

  const handleOpinionSubmit = useCallback(async (req: OpinionGenerateRequest) => {
    setStatus('running');
    setError(null);
    try {
      const result = await generateOpinion(req);
      setOpinionResult(result);
      setStatus('success');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : '观点生成失败');
      setStatus('error');
    }
  }, []);

  const handleReviewSubmit = useCallback(async (req: SemanticReviewRequest) => {
    setStatus('running');
    setError(null);
    try {
      const result = await reviewSemantic(req);
      setReviewResult(result);
      setStatus('success');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : '语义审核失败');
      setStatus('error');
    }
  }, []);

  const tabs: { id: ActiveTab; label: string }[] = [
    { id: 'article', label: '文章工作流' },
    { id: 'opinion', label: '观点生成' },
    { id: 'semantic_review', label: '语义审核' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">文章工作流</h2>
        <Button variant="ghost" size="sm" onClick={() => navigate('/')}>
          返回工作台
        </Button>
      </div>

      {/* Tab 选择 */}
      <div className="flex gap-1 border-b border-gray-200 pb-0">
        {tabs.map(tab => (
          <button
            key={tab.id}
            type="button"
            onClick={() => { setActiveTab(tab.id); setStatus('idle'); setError(null); }}
            className={`px-4 py-2 text-sm border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-blue-600 text-blue-600 font-medium'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧表单 */}
        <div className="lg:col-span-2">
          {activeTab === 'article' && (
            <ArticleWorkflowConfigForm
              value={articleDraft.draft}
              onChange={articleDraft.saveDraft}
              onSubmit={handleArticleSubmit}
              disabled={status === 'running'}
            />
          )}
          {activeTab === 'opinion' && (
            <OpinionConfigForm
              value={opinionDraft.draft}
              onChange={opinionDraft.saveDraft}
              onSubmit={handleOpinionSubmit}
              disabled={status === 'running'}
            />
          )}
          {activeTab === 'semantic_review' && (
            <SemanticReviewConfigForm
              value={reviewDraft.draft}
              onChange={reviewDraft.saveDraft}
              onSubmit={handleReviewSubmit}
              disabled={status === 'running'}
            />
          )}
        </div>

        {/* 右侧结果 */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <h3 className="text-sm font-medium text-gray-900">执行状态</h3>
            </CardHeader>
            <CardBody>
              <RunStatusBanner
                status={status}
                message={status === 'running' ? '正在处理中...' : undefined}
              />
              {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
            </CardBody>
          </Card>

          {status === 'success' && (
            <Card>
              <CardHeader>
                <h3 className="text-sm font-medium text-gray-900">执行结果</h3>
              </CardHeader>
              <CardBody className="max-h-[500px] overflow-y-auto">
                {activeTab === 'article' && articleResult && (
                  <ArticleWorkflowResultView result={articleResult} />
                )}
                {activeTab === 'opinion' && opinionResult && (
                  <OpinionResultView result={opinionResult} />
                )}
                {activeTab === 'semantic_review' && reviewResult && (
                  <SemanticReviewResultView result={reviewResult} />
                )}
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
