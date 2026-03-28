/**
 * Editorial Review Page — 编辑审阅页
 *
 * 双栏布局：左栏稿件全文预览（带批注）+ 右栏审核意见表单
 * 阶段口径：后端契约已定义，前端联调已接线
 */

import { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody, Button, Badge, Textarea, Select, Spinner } from '../components/ui';
import { Eye, ArrowLeft, CheckCircle2, AlertCircle, HelpCircle, FileText, Send, Lock, History } from 'lucide-react';
import { getTaskDetail, type TaskDetail } from '../api/tasks';
import {
  submitEditorialReview,
  getEditorialHistory,
  type ReviewDecision,
  type AnnotationType,
  type ReviewAnnotation,
  type EditorialHistoryItem,
} from '../api/editorial';
import { ApiError } from '../api/client';

// ============ 常量 ============

const ANNOTATION_TYPE_LABELS: Record<AnnotationType, string> = {
  suggest: '建议修改',
  must_fix: '必须修改',
  question: '有疑问',
};

const REWRITE_MODE_OPTIONS = [
  { value: 'expand_patch', label: '增补' },
  { value: 'dedupe_patch', label: '去重' },
  { value: 'deepen_patch', label: '深化' },
  { value: 'mixed_patch', label: '混合' },
];

const DECISION_MAP: Record<ReviewDecision, string> = {
  approved: '通过',
  conditional: '有条件通过',
  rejected: '退回改稿',
};

interface ParagraphItem {
  id: string;
  text: string;
}

interface LocalAnnotation extends ReviewAnnotation {
  id: string;
}

// ============ 组件 ============

export function EditorialReviewPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();

  // 数据加载
  const [task, setTask] = useState<TaskDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<EditorialHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // 交互状态
  const [decision, setDecision] = useState<ReviewDecision | ''>('');
  const [overallComment, setOverallComment] = useState('');
  const [annotations, setAnnotations] = useState<LocalAnnotation[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // 批注输入
  const [activeAnnotation, setActiveAnnotation] = useState<{ paragraphId: string } | null>(null);
  const [annotationType, setAnnotationType] = useState<AnnotationType>('suggest');
  const [annotationComment, setAnnotationComment] = useState('');

  // Patch 草稿
  const [patchMode, setPatchMode] = useState('expand_patch');
  const [patchLockedSections, setPatchLockedSections] = useState<string[]>([]);
  const [patchMustKeep, setPatchMustKeep] = useState('');
  const [patchChanges, setPatchChanges] = useState('');

  // 从任务数据提取段落
  const paragraphs: ParagraphItem[] = useMemo(() => {
    if (!task?.output_data) return [];
    const raw = task.output_data.paragraphs as Array<{ id: string; text: string }> | undefined;
    if (Array.isArray(raw)) return raw.map(p => ({ id: p.id, text: p.text }));
    const content = task.output_data.content as string | undefined;
    if (content) {
      return content.split('\n\n').filter(Boolean).map((t, i) => ({
        id: `p${i + 1}`,
        text: t,
      }));
    }
    return [];
  }, [task]);

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

  // 加载审阅历史
  useEffect(() => {
    if (!taskId) return;
    setHistoryLoading(true);
    getEditorialHistory(taskId)
      .then(res => setHistory(res.reviews))
      .catch(() => setHistory([]))
      .finally(() => setHistoryLoading(false));
  }, [taskId]);

  const addAnnotation = useCallback(() => {
    if (!activeAnnotation || !annotationComment.trim()) return;
    const newAnnotation: LocalAnnotation = {
      id: `ann-${Date.now()}`,
      paragraph_id: activeAnnotation.paragraphId,
      selected_text: '',
      type: annotationType,
      comment: annotationComment,
    };
    setAnnotations(prev => [...prev, newAnnotation]);
    setActiveAnnotation(null);
    setAnnotationComment('');
  }, [activeAnnotation, annotationType, annotationComment]);

  const removeAnnotation = useCallback((id: string) => {
    setAnnotations(prev => prev.filter(a => a.id !== id));
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!decision || !taskId) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      const patches = decision === 'rejected'
        ? patchChanges.split('\n').filter(Boolean).map(c => ({ paragraph_id: '', instruction: c }))
        : [];

      await submitEditorialReview({
        task_id: taskId,
        decision,
        overall_comment: overallComment,
        annotations: annotations.map(a => ({
          paragraph_id: a.paragraph_id,
          selected_text: a.selected_text,
          type: a.type,
          comment: a.comment,
        })),
        patches,
      });
      setSubmitted(true);
      // 刷新历史
      getEditorialHistory(taskId)
        .then(res => setHistory(res.reviews))
        .catch(() => {});
    } catch (e) {
      setSubmitError(e instanceof ApiError ? e.message : '提交审阅失败');
    } finally {
      setSubmitting(false);
    }
  }, [decision, taskId, overallComment, annotations, patchChanges]);

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
             <Eye size={20} className="text-brand-600" />
             审阅与批注
           </h2>
           <p className="text-xs text-slate-500 mt-1 ml-7">浏览文章、添加修改意见并给出最终通过或打回的决定</p>
        </div>
        <Button variant="ghost" size="sm" onClick={() => navigate(taskId ? `/tasks/${taskId}` : '/')} className="text-slate-500 hover:text-slate-900">
           <ArrowLeft size={16} className="mr-1.5" /> 返回任务详情
        </Button>
      </div>

      {submitted && (
        <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center gap-2 text-emerald-700">
           <CheckCircle2 size={16} /> <span className="text-sm font-medium">审阅意见已成功提交归档，并同步派发至对应队列。</span>
        </div>
      )}

      {submitError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
           <AlertCircle size={16} /> <span className="text-sm font-medium">{submitError}</span>
        </div>
      )}

      {paragraphs.length === 0 && (
        <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-center gap-2 text-amber-700">
           <AlertCircle size={16} /> <span className="text-sm font-medium">当前任务尚无可用段落数据，请检查上游工作流。</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
        {/* 左栏：稿件预览 + 批注 */}
        <div className="lg:col-span-7 flex flex-col min-h-0 overflow-hidden space-y-2">
          <Card className="flex-1 flex flex-col bg-white border-slate-200/60 shadow-sm overflow-hidden">
            <CardHeader className="py-3 px-5 bg-slate-50/80 border-b border-slate-100/80 flex justify-between items-center">
               <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
                 <FileText size={14} className="text-slate-400" /> 原文件与在线批注
               </h3>
               <Badge variant="info" size="sm" className="bg-slate-200 text-slate-600 border-0">{paragraphs.length} 段</Badge>
            </CardHeader>
            <CardBody className="p-5 space-y-5 overflow-y-auto bg-slate-50/30">
              {paragraphs.map((p, i) => {
                const paragraphAnnotations = annotations.filter(a => a.paragraph_id === p.id);
                return (
                  <div key={p.id} className="group relative bg-white p-5 rounded-xl border border-slate-200 hover:border-brand-200 hover:shadow-sm transition-all duration-200">
                    <div className="flex gap-4">
                      <span className="text-xs text-brand-600 font-mono bg-brand-50 px-2 py-1 rounded h-fit shrink-0 mt-0.5">§{i + 1}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-slate-700 leading-relaxed font-serif">{p.text}</p>
                        
                        {paragraphAnnotations.length > 0 && (
                          <div className="mt-4 space-y-2 border-t border-slate-100 pt-3">
                            {paragraphAnnotations.map(a => (
                              <div key={a.id} className={`flex items-start gap-3 p-3 rounded-lg text-xs ${
                                a.type === 'must_fix' ? 'bg-red-50/80 border border-red-100 text-red-800' :
                                a.type === 'question' ? 'bg-amber-50/80 border border-amber-100 text-amber-800' :
                                'bg-blue-50/80 border border-blue-100 text-blue-800'
                              }`}>
                                <Badge variant={a.type === 'must_fix' ? 'danger' : a.type === 'question' ? 'warning' : 'info'} size="sm" className="shadow-sm">
                                  {a.type === 'must_fix' ? <AlertCircle size={10} className="mr-1" /> : a.type === 'question' ? <HelpCircle size={10} className="mr-1" /> : <Eye size={10} className="mr-1" />}
                                  {ANNOTATION_TYPE_LABELS[a.type]}
                                </Badge>
                                <span className="flex-1 leading-relaxed font-medium">{a.comment}</span>
                                <button onClick={() => removeAnnotation(a.id)} className="text-slate-400 hover:text-red-500 hover:bg-red-100 p-1 rounded transition-colors">&times;</button>
                              </div>
                            ))}
                          </div>
                        )}
                        
                        {activeAnnotation?.paragraphId === p.id ? (
                          <div className="mt-4 p-4 border border-brand-200 rounded-lg bg-brand-50/30 space-y-3 shadow-inner">
                            <div className="flex gap-2">
                              {(['suggest', 'must_fix', 'question'] as AnnotationType[]).map(t => (
                                <button
                                  key={t}
                                  onClick={() => setAnnotationType(t)}
                                  className={`px-3 py-1.5 text-xs rounded-md shadow-sm transition-colors font-medium border ${annotationType === t ? 'bg-brand-600 text-white border-brand-600' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}`}
                                >
                                  {ANNOTATION_TYPE_LABELS[t]}
                                </button>
                              ))}
                            </div>
                            <input
                              className="w-full text-sm border border-slate-200 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 bg-white"
                              placeholder="输入批注内容 (按回车提交)..."
                              value={annotationComment}
                              onChange={e => setAnnotationComment(e.target.value)}
                              onKeyDown={e => e.key === 'Enter' && addAnnotation()}
                              autoFocus
                            />
                            <div className="flex gap-2 pt-1">
                              <Button size="sm" onClick={addAnnotation} className="h-8 text-xs px-4">保存批注</Button>
                              <Button variant="ghost" size="sm" onClick={() => setActiveAnnotation(null)} className="h-8 text-xs text-slate-500 border border-slate-200 bg-white hover:bg-slate-50">取消</Button>
                            </div>
                          </div>
                        ) : (
                          <button
                            onClick={() => setActiveAnnotation({ paragraphId: p.id })}
                            className="mt-3 text-xs font-semibold text-brand-600 bg-brand-50 hover:bg-brand-100 px-3 py-1.5 rounded-full opacity-0 group-hover:opacity-100 transition-all duration-200"
                          >
                            + 添加旁注
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </CardBody>
          </Card>
        </div>

        {/* 右栏：审核表单 */}
        <div className="lg:col-span-5 flex flex-col min-h-0 overflow-y-auto space-y-6 px-1">
          <Card className="shadow-sm border-slate-200/60 overflow-visible">
            <CardHeader className="py-3 px-5 bg-white border-b border-slate-100">
               <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
                 <CheckCircle2 size={16} className="text-brand-500" /> 最终决策面板
               </h3>
            </CardHeader>
            <CardBody className="p-5 space-y-5">
              <div>
                <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">执行流向动作</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {([
                    { value: 'approved' as const, label: '签发 (Approved)', desc: '发往成品库', color: 'border-emerald-500 bg-emerald-50 shadow-sm border-2' },
                    { value: 'conditional' as const, label: '带条件流转', desc: '作者修毕即完成', color: 'border-amber-500 bg-amber-50 shadow-sm border-2' },
                    { value: 'rejected' as const, label: '打回 (Rejected)', desc: '触发修正补丁', color: 'border-rose-500 bg-rose-50 shadow-sm border-2' },
                  ]).map(opt => (
                    <button
                      key={opt.value}
                      onClick={() => setDecision(opt.value)}
                      className={`p-3 border-2 rounded-xl text-left transition-all duration-200 flex flex-col items-start ${
                        decision === opt.value ? opt.color : 'border-slate-200 hover:border-slate-300 bg-white hover:bg-slate-50'
                      }`}
                    >
                      <div className={`text-sm font-bold ${decision === opt.value ? 'text-slate-900' : 'text-slate-700'}`}>{opt.label}</div>
                      <p className={`text-[0.65rem] mt-1 ${decision === opt.value ? 'text-slate-600 font-medium' : 'text-slate-400'}`}>{opt.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
              <Textarea
                label="总编评语 (Overall Comment)"
                value={overallComment}
                onChange={e => setOverallComment(e.target.value)}
                placeholder="对整篇稿件的总体评价，将会附在流转邮件中..."
                rows={3}
              />
            </CardBody>
          </Card>

          {decision === 'rejected' && (
            <Card className="shadow-sm border-rose-200/60 bg-rose-50/10 overflow-hidden relative">
              <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
                 <AlertCircle size={80} />
              </div>
              <CardHeader className="py-3 px-5 bg-rose-50 border-b border-rose-100 relative z-10">
                <h3 className="text-sm font-semibold text-rose-800 flex items-center gap-2">
                   <AlertCircle size={16} className="text-rose-500" />
                   AI 修正编排 (Patch Configuration)
                </h3>
              </CardHeader>
              <CardBody className="p-5 space-y-4 relative z-10">
                <Select
                  label="接管模式 (Rewrite Mode)"
                  value={patchMode}
                  onChange={e => setPatchMode(e.target.value)}
                  options={REWRITE_MODE_OPTIONS}
                />
                <div className="bg-white p-4 rounded-lg border border-rose-100 shadow-sm">
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5"><Lock size={12} className="text-amber-500"/> 强制段落锁存</p>
                  <div className="flex flex-wrap gap-2">
                    {paragraphs.map(p => (
                      <button
                        key={p.id}
                        onClick={() => setPatchLockedSections(prev =>
                          prev.includes(p.id) ? prev.filter(x => x !== p.id) : [...prev, p.id]
                        )}
                        className={`px-3 py-1 text-xs font-mono rounded-md shadow-sm transition-colors border ${patchLockedSections.includes(p.id) ? 'bg-amber-100 text-amber-800 border-amber-300/50 hover:bg-amber-200 font-semibold' : 'bg-slate-50 text-slate-500 border-slate-200 hover:bg-slate-100'}`}
                      >
                        §{p.id.replace('p','')}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Textarea
                    label="约束信息注入 (每行一条)"
                    value={patchMustKeep}
                    onChange={e => setPatchMustKeep(e.target.value)}
                    placeholder="CDR-SB 主要终点&#10;ARIA-E 发生率"
                    rows={4}
                  />
                  <Textarea
                    label="修正行为指令 (每行一条)"
                    value={patchChanges}
                    onChange={e => setPatchChanges(e.target.value)}
                    placeholder="§3 增补亚组分析数据&#10;§4 补充 EMA 批准信息"
                    rows={4}
                  />
                </div>
              </CardBody>
            </Card>
          )}

          {/* 审核历史 */}
          <Card className="shadow-sm border-slate-200/60 shrink-0">
            <CardHeader className="py-3 px-5 bg-white border-b border-slate-100">
               <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
                 <History size={14} className="text-indigo-500" />
                 审查与流转记录
               </h3>
            </CardHeader>
            <CardBody className="p-4">
              {historyLoading ? (
                <div className="flex justify-center py-6 text-slate-300"><Spinner size="md" /></div>
              ) : history.length > 0 ? (
                <div className="space-y-3">
                  {history.map((r, i) => (
                    <div key={r.review_id} className="flex flex-col sm:flex-row sm:items-center justify-between text-sm p-4 rounded-xl border border-slate-100 shadow-sm bg-slate-50 gap-3 hover:bg-white hover:border-slate-200 transition-colors">
                      <div className="flex items-center gap-3">
                        <span className="text-xs font-mono font-medium text-slate-400 bg-slate-200/50 px-2 py-0.5 rounded">R{history.length - i}</span>
                        <Badge variant={r.decision === 'rejected' ? 'danger' : r.decision === 'conditional' ? 'warning' : 'success'} size="md" className="shadow-sm">
                          {DECISION_MAP[r.decision]}
                        </Badge>
                        <span className="text-sm font-medium text-slate-700 max-w-[200px] truncate">{r.overall_comment || <span className="text-slate-400 italic">无批语</span>}</span>
                      </div>
                      <span className="text-xs text-slate-500 font-mono flex items-center gap-1.5"><History size={12} /> {new Date(r.created_at).toLocaleString('zh-CN')}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-6 text-slate-400">
                   <History size={24} className="mb-2 opacity-50" />
                   <p className="text-xs font-medium">尚无审查干预发生，系统处于初版等待状态。</p>
                </div>
              )}
            </CardBody>
          </Card>

          <Button
            className="w-full shadow-md h-12 text-sm"
            disabled={!decision || submitting || submitted}
            onClick={handleSubmit}
          >
            {submitting ? <><Spinner size="sm" className="mr-2 text-white" /> 签发编审流程中...</> : submitted ? <><CheckCircle2 size={16} className="mr-2" /> 签核完毕</> : <><Send size={16} className="mr-2" /> 执行最终裁决进入管线</>}
          </Button>
        </div>
      </div>
    </div>
  );
}
