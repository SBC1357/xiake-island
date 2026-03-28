/**
 * New Task Page — 新建写作任务页
 * 
 * 任务基本信息 + 工作流选择 + 创建方式（一键/分步）+ 草稿恢复
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody, Button, Input, Select, Textarea, Badge, Spinner } from '../components/ui';
import { listProducts } from '../api/evidence';
import { executeStandardChainWorkflow } from '../api/workflow';
import { ApiError } from '../api/client';
import { PenTool, LayoutTemplate, Play, Settings2 } from 'lucide-react';

interface TaskFormData {
  taskName: string;
  productId: string;
  customTopic: string;
  workflow: 'standard_chain' | 'article';
  audience: string;
  projectName: string;
  targetWordCount: number;
  register: string;
  notes: string;
}

const DRAFT_KEY = 'xiakedao_new_task_draft';

function loadDraft(): TaskFormData | null {
  try {
    const stored = localStorage.getItem(DRAFT_KEY);
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
}

function saveDraft(data: TaskFormData) {
  localStorage.setItem(DRAFT_KEY, JSON.stringify(data));
}

const DEFAULT_FORM: TaskFormData = {
  taskName: '',
  productId: '',
  customTopic: '',
  workflow: 'standard_chain',
  audience: '医学专业人士',
  projectName: '',
  targetWordCount: 2000,
  register: 'academic',
  notes: '',
};

const AUDIENCE_OPTIONS = [
  { value: '医学专业人士', label: '医学专业人士' },
  { value: '临床医生', label: '临床医生' },
  { value: '药学从业者', label: '药学从业者' },
  { value: '医学研究者', label: '医学研究者' },
  { value: '医学生', label: '医学生' },
  { value: '非专业公众', label: '非专业公众' },
];

const REGISTER_OPTIONS = [
  { value: 'academic', label: '学术型' },
  { value: 'clinical', label: '临床型' },
  { value: 'educational', label: '教育科普' },
  { value: 'promotional', label: '推广传播' },
];

export function NewTaskPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState<TaskFormData>(() => loadDraft() || DEFAULT_FORM);
  const [products, setProducts] = useState<string[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasDraft, setHasDraft] = useState(!!loadDraft());

  useEffect(() => {
    listProducts()
      .then(res => setProducts(res.products))
      .catch(() => {})
      .finally(() => setProductsLoading(false));
  }, []);

  const updateField = useCallback(<K extends keyof TaskFormData>(key: K, value: TaskFormData[K]) => {
    setForm(prev => {
      const next = { ...prev, [key]: value };
      saveDraft(next);
      return next;
    });
  }, []);

  const canSubmit = form.taskName.trim() && (form.productId || form.customTopic.trim()) && form.audience && form.targetWordCount > 0;

  const handleOneClick = useCallback(async () => {
    if (!canSubmit) return;

    if (form.workflow === 'article') {
      localStorage.removeItem(DRAFT_KEY);
      navigate('/workflow/article');
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const result = await executeStandardChainWorkflow({
        product_id: form.productId || form.customTopic,
        audience: form.audience,
        project_name: form.projectName || form.taskName,
        target_word_count: form.targetWordCount,
        register: form.register,
        metadata: {
          ...(form.notes ? { notes: form.notes } : {}),
          _input_source: form.productId ? 'product' : 'custom_topic',
        },
      });
      localStorage.removeItem(DRAFT_KEY);
      navigate(`/tasks/${result.task_id}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : '任务创建失败');
    } finally {
      setSubmitting(false);
    }
  }, [canSubmit, form, navigate]);

  const handleStepByStep = useCallback(() => {
    sessionStorage.setItem('xiakedao_chain_init', JSON.stringify({
      productId: form.productId || form.customTopic,
      audience: form.audience,
      projectName: form.projectName || form.taskName,
      targetWordCount: form.targetWordCount,
      register: form.register,
    }));
    navigate('/tasks/new/chain');
  }, [form, navigate]);

  const handleClearDraft = useCallback(() => {
    localStorage.removeItem(DRAFT_KEY);
    setForm(DEFAULT_FORM);
    setHasDraft(false);
  }, []);

  const productOptions = products.map(p => ({ value: p, label: p }));

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-300">
      <div className="flex items-center justify-between mt-2">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">新建写作任务</h2>
          <p className="text-slate-500 mt-1.5 text-sm">配置基础参数并选择要执行的工作流引擎以开始自动化创作。</p>
        </div>
        {hasDraft && (
          <div className="flex items-center gap-3 bg-brand-50 px-4 py-2 rounded-lg border border-brand-100">
            <span className="flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-brand-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-500"></span>
            </span>
            <span className="text-xs text-brand-700 font-medium">检测到未完成的草稿</span>
            <Button variant="ghost" size="sm" onClick={handleClearDraft} className="text-brand-600 hover:text-brand-800 hover:bg-brand-100 -mr-2 ml-1 h-6 px-2">
               &times; 清除
            </Button>
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <div className="text-red-500 bg-white p-1 rounded-full border border-red-100 shrink-0">
             <Settings2 size={16} /> 
          </div>
          <p className="text-sm text-red-700 font-medium">{error}</p>
        </div>
      )}

      <div className="space-y-6">
        <Card className="overflow-hidden">
          <CardHeader className="bg-slate-50/80 border-b-slate-100">
            <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
              <PenTool size={16} className="text-brand-600" />
              1. 设定任务与目标
            </h3>
          </CardHeader>
          <CardBody className="p-6 md:p-8 space-y-6">
            <div className="max-w-md">
              <Input
                label="任务名称"
                value={form.taskName}
                onChange={e => updateField('taskName', e.target.value)}
                placeholder="例如：仑卡奈单抗最新临床综述"
                required
              />
            </div>
            
            <div className="bg-slate-50 p-5 rounded-xl border border-slate-100 space-y-5">
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">输入源配置</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <Select
                  label="关联藏经阁产品线"
                  value={form.productId}
                  onChange={e => updateField('productId', e.target.value)}
                  options={[{ value: '', label: productsLoading ? '数据加载中...' : '— 请选择产品线 —' }, ...productOptions]}
                  hint="优先选择系统内已有知识库产品"
                />
                <Input
                  label="自定义主题 (回退方案)"
                  value={form.customTopic}
                  onChange={e => updateField('customTopic', e.target.value)}
                  placeholder="仅当关联产品线无法满足时手填"
                  hint="产品线和自定义主题二选一即可"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 pt-2">
               <Select
                label="目标受众"
                value={form.audience}
                onChange={e => updateField('audience', e.target.value)}
                options={AUDIENCE_OPTIONS}
                required
              />
              <Select
                label="语体等级"
                value={form.register}
                onChange={e => updateField('register', e.target.value)}
                options={REGISTER_OPTIONS}
                required
              />
              <Input
                label="目标字数 (字)"
                type="number"
                min="100"
                step="100"
                value={String(form.targetWordCount)}
                onChange={e => updateField('targetWordCount', Number(e.target.value))}
                required
              />
            </div>

            <div className="pt-2">
              <Textarea
                label="附加指令或背景要求 (Prompt 注入)"
                value={form.notes}
                onChange={e => updateField('notes', e.target.value)}
                placeholder="在这里写下对此篇稿件的特定侧重点、语气的附加要求..."
                rows={3}
              />
            </div>
          </CardBody>
        </Card>

        <Card className="overflow-hidden">
          <CardHeader className="bg-slate-50/80 border-b-slate-100">
            <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
              <LayoutTemplate size={16} className="text-brand-600" />
              2. 配置工作流引擎
            </h3>
          </CardHeader>
          <CardBody className="p-6 md:p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => updateField('workflow', 'standard_chain')}
                className={`relative p-5 border-2 rounded-xl text-left transition-all duration-200 flex flex-col items-start ${
                  form.workflow === 'standard_chain'
                    ? 'border-brand-500 bg-brand-50/50 shadow-sm'
                    : 'border-slate-200 hover:border-brand-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center justify-between w-full mb-2">
                   <div className="font-semibold text-slate-900 text-base">标准图谱六段链</div>
                   <Badge variant="success">推荐 / 稳定版</Badge>
                </div>
                <p className="text-sm text-slate-500 mb-4 h-10">
                  结构化执行大文章：大纲规划 → 检索证据 → 草稿 → 润色改写 → 质量内审
                </p>
                <div className="mt-auto w-full flex items-center gap-1.5 text-xs font-mono text-slate-400">
                   <span>Planner</span><span className="text-slate-300">→</span><span>Evidence</span><span className="text-slate-300">→</span><span>Writer</span>
                </div>
                {form.workflow === 'standard_chain' && (
                  <div className="absolute inset-0 border-2 border-brand-500 rounded-xl pointer-events-none"></div>
                )}
              </button>
              
              <button
                type="button"
                onClick={() => updateField('workflow', 'article')}
                className={`relative p-5 border-2 rounded-xl text-left transition-all duration-200 flex flex-col items-start ${
                  form.workflow === 'article'
                    ? 'border-brand-500 bg-brand-50/50 shadow-sm'
                    : 'border-slate-200 hover:border-brand-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center justify-between w-full mb-2">
                   <div className="font-semibold text-slate-900 text-base">通用文章直出工作流</div>
                   <Badge variant="default">轻量 / Beta</Badge>
                </div>
                <p className="text-sm text-slate-500 mb-4 h-10">
                  依赖通用底座的连贯直出，无复杂图谱环节。适合新闻快讯与短文案。
                </p>
                <div className="mt-auto w-full flex items-center gap-1.5 text-xs font-mono text-slate-400">
                   <span>Direct Writer</span><span className="text-slate-300">→</span><span>Semantic Check</span>
                </div>
                {form.workflow === 'article' && (
                   <div className="absolute inset-0 border-2 border-brand-500 rounded-xl pointer-events-none"></div>
                )}
              </button>
            </div>
          </CardBody>
        </Card>

        {/* 启动操作区 */}
        <div className="flex bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden divide-x divide-slate-100">
          <div className="flex-1 p-6 lg:p-8 flex flex-col">
            <h4 className="font-semibold text-slate-900 flex items-center gap-2 mb-2">
               <Settings2 size={16} className="text-slate-400" /> 分步交互模式
            </h4>
            <p className="text-sm text-slate-500 mb-6 flex-1">
              由人类编辑主导的工作流，可在生成大纲、生成初稿等核心节点进行人工介入调优。适合长篇深度专栏。
            </p>
            <Button
              variant="secondary"
              className="w-full justify-center h-11"
              onClick={handleStepByStep}
              disabled={!canSubmit || submitting || form.workflow === 'article'}
            >
              {form.workflow === 'article' ? '仅限六段链可用' : '进入分步控制台工作区'}
            </Button>
          </div>
          
          <div className="flex-1 p-6 lg:p-8 flex flex-col bg-brand-50/30">
            <h4 className="font-semibold text-brand-900 flex items-center gap-2 mb-2">
               <Play size={16} className="text-brand-500" /> 自动化一键投产
            </h4>
            <p className="text-sm text-brand-700/70 mb-6 flex-1">
              配置封顶，全自动跑通从规划到交付全流程，中途无需人工干预。适合大规模资讯流水线或试跑初版。
            </p>
            <Button
              className="w-full justify-center h-11 shadow-sm"
              onClick={handleOneClick}
              disabled={!canSubmit || submitting}
            >
              {submitting ? <><Spinner size="sm" className="mr-2 text-white" /> 调度创建中...</> : <><Play size={16} className="mr-2" /> 发起全自动执行</>}
            </Button>
          </div>
        </div>

      </div>
    </div>
  );
}
