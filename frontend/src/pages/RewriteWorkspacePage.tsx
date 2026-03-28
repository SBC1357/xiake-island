/**
 * Rewrite Workspace Page — 改稿工作区
 *
 * 三栏布局：左栏当前稿件 + 中栏改稿控制面板 + 右栏冻结 brief 与历史
 * 阶段口径：后端契约已定义，前端联调已接线
 */

import { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody, CardFooter, Button, Select, Badge, Spinner } from '../components/ui';
import { Edit3, ArrowLeft, Lock, GitMerge, FileText, CheckCircle2, AlertCircle, History, Zap, Settings2, ShieldCheck, ArrowRight } from 'lucide-react';
import { getTaskDetail, type TaskDetail } from '../api/tasks';
import {
  executeRewrite,
  getRewriteHistory,
  type RewriteMode,
  type ParagraphAction,
  type FrozenBrief,
  type RewriteExecuteResponse,
  type RewriteHistoryItem,
} from '../api/rewrite';
import { ApiError } from '../api/client';

// ============ 常量 ============

const MODE_OPTIONS = [
  { value: 'expand_patch', label: '增补 (expand)' },
  { value: 'dedupe_patch', label: '去重 (dedupe)' },
  { value: 'deepen_patch', label: '深化 (deepen)' },
  { value: 'mixed_patch', label: '混合 (mixed)' },
];

const DEEPEN_DIMENSIONS = ['机制', '证据', '对比', '边界', '临床推导'];

const ACTION_LABELS: Record<ParagraphAction, string> = {
  default: '默认',
  lock: '锁定',
  expand: '增补',
  compress: '压缩',
  deepen: '深化',
};

interface ParagraphItem {
  id: string;
  text: string;
  locked: boolean;
}

interface ParagraphState {
  action: ParagraphAction;
  instruction: string;
}

// ============ 组件 ============

export function RewriteWorkspacePage() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();

  // 数据加载
  const [task, setTask] = useState<TaskDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<RewriteHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // 交互状态
  const [mode, setMode] = useState<RewriteMode>('expand_patch');
  const [deepenDimensions, setDeepenDimensions] = useState<string[]>([]);
  const [paragraphStates, setParagraphStates] = useState<Record<string, ParagraphState>>({});
  const [result, setResult] = useState<RewriteExecuteResponse | null>(null);
  const [executing, setExecuting] = useState(false);
  const [executeError, setExecuteError] = useState<string | null>(null);

  // 从任务数据提取段落和 brief
  const paragraphs: ParagraphItem[] = useMemo(() => {
    if (!task?.output_data) return [];
    const raw = task.output_data.paragraphs as Array<{ id: string; text: string; locked?: boolean }> | undefined;
    if (Array.isArray(raw)) return raw.map(p => ({ id: p.id, text: p.text, locked: !!p.locked }));
    // 若 output_data 有 content 字段，按段落拆分
    const content = task.output_data.content as string | undefined;
    if (content) {
      return content.split('\n\n').filter(Boolean).map((t, i) => ({
        id: `p${i + 1}`,
        text: t,
        locked: false,
      }));
    }
    return [];
  }, [task]);

  const brief: FrozenBrief = useMemo(() => {
    const meta = task?.metadata as Record<string, unknown> | undefined;
    const raw = meta?.brief as Partial<FrozenBrief> | undefined;
    return {
      locked_sections: raw?.locked_sections ?? [],
      must_keep_points: raw?.must_keep_points ?? [],
      must_delete_points: raw?.must_delete_points ?? [],
      forbidden_topics: raw?.forbidden_topics ?? [],
      word_count_target: raw?.word_count_target ?? { min: 0, max: 0 },
      evidence_gaps: raw?.evidence_gaps ?? [],
    };
  }, [task]);

  // 初始化段落状态
  useEffect(() => {
    if (paragraphs.length > 0 && Object.keys(paragraphStates).length === 0) {
      setParagraphStates(Object.fromEntries(
        paragraphs.map(p => [p.id, { action: p.locked ? 'lock' as ParagraphAction : 'default' as ParagraphAction, instruction: '' }])
      ));
    }
  }, [paragraphs, paragraphStates]);

  // 加载任务详情
  useEffect(() => {
    if (!taskId) return;
    setLoading(true);
    setError(null);
    getTaskDetail(taskId)
      .then(detail => setTask(detail))
      .catch(e => setError(e instanceof ApiError ? e.message : '加载任务详情失败'))
      .finally(() => setLoading(false));
  }, [taskId]);

  // 加载改稿历史
  useEffect(() => {
    if (!taskId) return;
    setHistoryLoading(true);
    getRewriteHistory(taskId)
      .then(res => setHistory(res.history))
      .catch(() => setHistory([]))
      .finally(() => setHistoryLoading(false));
  }, [taskId]);

  // Gate 校验
  const gateChecks = useMemo(() => [
    { label: '已有冻结 Brief', pass: brief.must_keep_points.length > 0 || brief.locked_sections.length > 0 },
    { label: '已选择改稿模式', pass: !!mode },
    { label: '已标注锁定段落', pass: Object.values(paragraphStates).some(s => s.action === 'lock') },
    { label: '已列出必保留信息点', pass: brief.must_keep_points.length > 0 },
    { label: '已列出证据缺口', pass: brief.evidence_gaps.length > 0 },
  ], [mode, paragraphStates, brief]);

  const allGatesPassed = gateChecks.every(c => c.pass);

  const setParagraphAction = useCallback((id: string, action: ParagraphAction) => {
    setParagraphStates(prev => ({ ...prev, [id]: { ...prev[id], action } }));
  }, []);

  const setParagraphInstruction = useCallback((id: string, instruction: string) => {
    setParagraphStates(prev => ({ ...prev, [id]: { ...prev[id], instruction } }));
  }, []);

  const handleExecute = useCallback(async () => {
    if (!taskId) return;
    setExecuting(true);
    setExecuteError(null);
    try {
      const response = await executeRewrite({
        task_id: taskId,
        mode,
        paragraph_instructions: Object.entries(paragraphStates).map(([id, s]) => ({
          paragraph_id: id,
          action: s.action,
        })),
        brief,
      });
      setResult(response);
      // 刷新历史
      getRewriteHistory(taskId)
        .then(res => setHistory(res.history))
        .catch(() => {});
    } catch (e) {
      setExecuteError(e instanceof ApiError ? e.message : '改稿执行失败');
    } finally {
      setExecuting(false);
    }
  }, [taskId, mode, paragraphStates, brief]);

  // ============ 渲染 ============

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12 flex justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <Button variant="secondary" onClick={() => navigate(taskId ? `/tasks/${taskId}` : '/')}>返回</Button>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto px-4 py-6 h-[calc(100vh-64px)] flex flex-col animate-in fade-in duration-300">
      <div className="flex items-center justify-between mb-6 shrink-0">
        <div>
           <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
             <Edit3 size={20} className="text-brand-600" />
             AI 改稿工作台
           </h2>
           <p className="text-xs text-slate-500 mt-1 ml-7">Rewrite & Optimization Workspace</p>
        </div>
        <Button variant="ghost" size="sm" onClick={() => navigate(taskId ? `/tasks/${taskId}` : '/')} className="text-slate-500 hover:text-slate-900">
           <ArrowLeft size={16} className="mr-1.5" /> 返回任务详情
        </Button>
      </div>

      {paragraphs.length === 0 && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-sm text-yellow-700">当前任务尚无可用段落数据，请确认任务已生成正文。</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
        {/* 左栏：当前稿件全文 */}
        <div className="lg:col-span-4 flex flex-col min-h-0 space-y-2">
          <Card className="flex-1 flex flex-col bg-white border-slate-200/60 shadow-sm overflow-hidden">
            <CardHeader className="py-3 px-5 bg-slate-50/80 border-b border-slate-100/80 flex justify-between items-center">
               <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
                 <FileText size={14} className="text-slate-400" /> 当前主稿
               </h3>
               <Badge variant="info" size="sm" className="bg-slate-200 text-slate-600 border-0">{paragraphs.length} 段</Badge>
            </CardHeader>
            <CardBody className="p-4 space-y-4 overflow-y-auto bg-slate-50/30">
              {paragraphs.map((p, i) => {
                const state = paragraphStates[p.id] ?? { action: 'default' as ParagraphAction, instruction: '' };
                const isLocked = state.action === 'lock';
                return (
                  <div key={p.id} className={`p-4 rounded-xl border text-sm transition-colors ${isLocked ? 'border-amber-200 bg-amber-50/50 shadow-sm' : 'border-slate-200 bg-white hover:border-brand-200 hover:shadow-sm'}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs text-brand-600 font-mono bg-brand-50 px-1.5 py-0.5 rounded">§{i + 1}</span>
                      {isLocked && <Badge variant="warning" size="sm" className="bg-amber-100 text-amber-700 border-amber-200"><Lock size={10} className="mr-1" /> 已锁定</Badge>}
                    </div>
                    <p className={`text-slate-700 leading-relaxed font-serif ${isLocked ? 'opacity-80' : ''}`}>{p.text}</p>
                    <div className="flex gap-1.5 mt-4 pt-3 border-t border-slate-100">
                      {(['default', 'lock', 'expand', 'compress', 'deepen'] as ParagraphAction[]).map(a => (
                        <button
                          key={a}
                          onClick={() => setParagraphAction(p.id, a)}
                          className={`px-2.5 py-1 text-xs rounded-md font-medium transition-colors ${state.action === a ? (a === 'lock' ? 'bg-amber-100 text-amber-700' : 'bg-brand-100 text-brand-700') : 'bg-slate-50 text-slate-500 hover:bg-slate-100'}`}
                        >
                          {ACTION_LABELS[a]}
                        </button>
                      ))}
                    </div>
                    {(state.action === 'expand' || state.action === 'deepen') && (
                      <input
                        className="mt-3 w-full text-xs border border-brand-200 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500/20 bg-brand-50/30 text-brand-900 placeholder-brand-300"
                        placeholder={state.action === 'expand' ? '输入增补指令 (例如：增加仑卡奈单抗的用药剂量说明)...' : '输入深化维度 (例如：对比不同指南的推荐等级)...'}
                        value={state.instruction}
                        onChange={e => setParagraphInstruction(p.id, e.target.value)}
                      />
                    )}
                  </div>
                );
              })}
            </CardBody>
          </Card>
        </div>

        {/* 中栏：改稿控制面板 */}
        <div className="lg:col-span-4 flex flex-col min-h-0 overflow-y-auto space-y-6 px-1">
          <Card className="shadow-sm border-slate-200/60 overflow-visible">
            <CardHeader className="py-3 px-5 bg-white border-b border-slate-100 flex items-center gap-2">
               <Settings2 size={16} className="text-slate-400" />
               <h3 className="text-sm font-semibold text-slate-800">模型接管参数</h3>
            </CardHeader>
            <CardBody className="space-y-3">
              <Select
                label="模式选择"
                value={mode}
                onChange={e => setMode(e.target.value as RewriteMode)}
                options={MODE_OPTIONS}
              />
              {mode === 'deepen_patch' && (
                <div>
                  <p className="text-xs text-gray-500 mb-1">深化维度</p>
                  <div className="flex flex-wrap gap-1">
                    {DEEPEN_DIMENSIONS.map(d => (
                      <button
                        key={d}
                        onClick={() => setDeepenDimensions(prev => prev.includes(d) ? prev.filter(x => x !== d) : [...prev, d])}
                        className={`px-2 py-1 text-xs rounded ${deepenDimensions.includes(d) ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'}`}
                      >
                        {d}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </CardBody>
          </Card>

          <Card className="shadow-sm border-slate-200/60">
            <CardHeader className="py-3 px-5 bg-white border-b border-slate-100 flex items-center gap-2">
               <ShieldCheck size={16} className="text-emerald-500" />
               <h3 className="text-sm font-semibold text-slate-800">策略验证门控 (Gate checks)</h3>
            </CardHeader>
            <CardBody className="space-y-2 p-5 bg-slate-50/50">
              {gateChecks.map(c => (
                <div key={c.label} className="flex items-center gap-3 text-sm p-2 rounded-lg bg-white border border-slate-100 shadow-sm">
                  <span className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${c.pass ? 'bg-emerald-100 text-emerald-600' : 'bg-red-50 text-red-500'}`}>
                    {c.pass ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />}
                  </span>
                  <span className={c.pass ? 'text-slate-700 font-medium' : 'text-slate-500 line-through'}>{c.label}</span>
                </div>
              ))}
              <div className="pt-4 mt-2 border-t border-slate-200">
                <Button
                  className="w-full h-11 text-sm shadow-sm"
                  disabled={!allGatesPassed || executing}
                  onClick={handleExecute}
                >
                  {executing ? <><Spinner size="sm" className="mr-2 text-white" /> AI 介入改写中...</> : <><Zap size={16} className="mr-2" /> 投产执行 (Execute)</>}
                </Button>
                {executeError && <p className="text-xs text-red-600 mt-3 p-2 bg-red-50 rounded border border-red-100">{executeError}</p>}
              </div>
            </CardBody>
          </Card>

          {result && (
            <Card className="border-brand-200 shadow-sm overflow-hidden">
               <div className="h-1 bg-brand-500 w-full"></div>
              <CardHeader className="py-3 px-5 bg-brand-50/50 border-b border-brand-100 flex items-center justify-between">
                <h3 className="text-sm font-semibold text-brand-900 flex items-center gap-2">
                   <GitMerge size={16} className="text-brand-600" />
                   执行摘要
                </h3>
              </CardHeader>
              <CardBody className="space-y-4 p-5">
                <div className="flex items-center gap-3 p-3 bg-white rounded-lg border border-slate-100 shadow-sm">
                  <Badge variant={result.status === 'completed' ? 'success' : result.status === 'failed' ? 'danger' : 'info'} size="md" className={result.status === 'completed' ? 'bg-emerald-100 text-emerald-800' : ''}>
                    {result.status === 'completed' ? '处理完成' : result.status === 'failed' ? '处理异常' : '处理中'}
                  </Badge>
                  <span className="text-sm text-slate-600 font-medium">
                    体积变化： <span className={result.word_delta > 0 ? 'text-emerald-600' : 'text-amber-600'}>{result.word_delta > 0 ? '+' : ''}{result.word_delta} 原生词</span>
                  </span>
                </div>
                {result.error && <p className="text-xs text-red-600 p-2 bg-red-50 rounded">{result.error}</p>}
                {result.paragraphs.length > 0 && (
                  <div className="space-y-3 max-h-60 overflow-y-auto pr-2">
                    {result.paragraphs.filter(p => p.status !== 'unchanged').map(p => (
                      <div key={p.paragraph_id} className="text-xs p-3 rounded-xl bg-white border border-slate-200/60 shadow-sm">
                        <div className="flex items-center justify-between mb-2">
                           <span className="text-slate-400 font-mono">ID: {p.paragraph_id}</span>
                           <Badge variant="success" size="sm" className="bg-emerald-50 text-emerald-700">{p.status}</Badge>
                        </div>
                        <p className="text-slate-700 leading-relaxed font-serif">{p.new_text}</p>
                      </div>
                    ))}
                  </div>
                )}
              </CardBody>
              <CardFooter className="bg-slate-50 border-t border-slate-100 flex justify-end">
                <Button variant="secondary" size="sm" onClick={() => navigate(taskId ? `/tasks/${taskId}/compare` : '/')} className="bg-white shadow-sm hover:text-brand-600">
                  详情对比审计 <ArrowRight size={14} className="ml-1.5" />
                </Button>
              </CardFooter>
            </Card>
          )}
        </div>

        {/* 右栏：冻结 Brief + 历史 */}
        <div className="lg:col-span-4 flex flex-col min-h-0 overflow-y-auto space-y-6">
          <Card className="shadow-sm border-slate-200/60 flex-1 flex flex-col">
            <CardHeader className="py-3 px-5 bg-slate-50/80 border-b border-slate-100">
               <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
                 <Lock size={14} className="text-amber-500" />
                 任务契约约束 (Frozen Brief)
               </h3>
            </CardHeader>
            <CardBody className="space-y-5 flex-1 p-5 overflow-y-auto">
              {brief.locked_sections.length > 0 && (
                <div>
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">锁定段落与内容</p>
                  <div className="flex flex-wrap gap-1.5">
                    {brief.locked_sections.map(s => <Badge key={s} variant="warning" size="sm" className="bg-amber-100 text-amber-800 border-amber-200">{s}</Badge>)}
                  </div>
                </div>
              )}
              {brief.must_keep_points.length > 0 && (
                <div>
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">保留信息锚点</p>
                  <ul className="text-sm text-slate-700 space-y-1.5 bg-slate-50 p-3 rounded-lg border border-slate-100">
                    {brief.must_keep_points.map((p, i) => <li key={i} className="flex gap-2 relative pl-3 before:content-[''] before:absolute before:left-0 before:top-2 before:w-1.5 before:h-1.5 before:bg-brand-400 before:rounded-full"><span className="leading-snug">{p}</span></li>)}
                  </ul>
                </div>
              )}
              {brief.word_count_target.min > 0 && (
                <div>
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">系统推算边界</p>
                  <div className="flex items-center gap-2 p-3 bg-slate-50 rounded-lg border border-slate-100">
                     <span className="text-2xl font-mono text-slate-800">{brief.word_count_target.min}</span>
                     <span className="text-slate-400">一</span>
                     <span className="text-2xl font-mono text-slate-800">{brief.word_count_target.max}</span>
                     <span className="text-sm text-slate-500 ml-1">Tokens</span>
                  </div>
                </div>
              )}
              {brief.evidence_gaps.length > 0 && (
                <div>
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">图谱探测缺口 / 幻觉风险</p>
                  <div className="space-y-2">
                    {brief.evidence_gaps.map((g, i) => (
                      <div key={i} className="text-xs bg-red-50 text-red-700 p-2.5 rounded border border-red-100 flex gap-2">
                         <AlertCircle size={14} className="shrink-0 mt-0.5 text-red-500" />
                         <span className="leading-relaxed"><strong className="font-semibold text-red-800">§{g.position}:</strong> {g.missing}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {brief.locked_sections.length === 0 && brief.must_keep_points.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center opacity-50 py-8">
                   <Lock size={32} className="text-slate-300 mb-3" />
                   <p className="text-sm text-slate-500 font-medium">无硬性契约继承</p>
                </div>
              )}
            </CardBody>
          </Card>

          <Card className="shadow-sm border-slate-200/60 shrink-0">
            <CardHeader className="py-3 px-5 bg-white border-b border-slate-100">
               <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
                 <History size={14} className="text-indigo-500" />
                 衍生树快照
               </h3>
            </CardHeader>
            <CardBody>
              {historyLoading ? (
                <div className="flex justify-center py-4"><Spinner size="sm" /></div>
              ) : history.length > 0 ? (
                <div className="space-y-2">
                  {history.map(v => (
                    <div key={v.rewrite_task_id} className="flex items-center justify-between text-sm p-3 rounded-lg border border-slate-100 bg-slate-50 hover:bg-white hover:border-slate-200 transition-colors shadow-sm cursor-pointer group">
                      <div className="flex items-center gap-3">
                        <Badge variant="default" size="sm" className="font-mono bg-white border-slate-200 group-hover:border-slate-300">{v.version_label}</Badge>
                        <span className="text-slate-700 font-medium">{v.mode}</span>
                        <span className={`text-xs font-mono font-medium px-1.5 py-0.5 rounded ${v.word_delta > 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                          {v.word_delta > 0 ? '+' : ''}{v.word_delta} 字
                        </span>
                      </div>
                      <span className="text-xs text-slate-400 font-mono">{new Date(v.created_at).toLocaleString('zh-CN')}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-400 text-center py-2">暂无历史记录</p>
              )}
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
