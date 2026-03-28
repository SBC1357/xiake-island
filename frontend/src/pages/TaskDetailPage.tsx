/**
 * Task Detail Page — 任务详情页
 * 
 * 任务头卡 + 六段链步骤时间线 + 每步输入/输出摘要 + 错误日志 + 产物区 + 复制任务入口
 */

import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Card, CardHeader, CardBody, Button, Badge, Spinner } from '../components/ui';
import { getTaskDetail, copyTask, type TaskDetail } from '../api/tasks';
import { ApiError } from '../api/client';
import { PlayCircle, CheckCircle2, AlertCircle, Clock, Copy, Plus, ArrowLeft, TerminalSquare, GitCompare, Edit3, Eye, FileJson } from 'lucide-react';

const CHAIN_STEP_LABELS: Record<string, string> = {
  evidence: '调取资料形成故事线',
  planning: '形成大纲',
  writing: '分章节合成内容',
  drafting: '生成全文',
  quality: '非人工审核',
  delivery: '最终成稿交付',
  opinion: '文章观点生成',
  semantic_review: '语义智能审核',
  orchestrator: '文章总控调度',
};

function statusVariant(status: string): 'success' | 'danger' | 'warning' | 'info' | 'default' {
  switch (status) {
    case 'completed': return 'success';
    case 'failed': return 'danger';
    case 'running': return 'info';
    case 'pending': return 'warning';
    default: return 'default';
  }
}

function StatusIcon({ status, className = '', size = 16 }: { status: string; className?: string; size?: number }) {
  switch (status) {
    case 'completed': return <CheckCircle2 size={size} className={`text-emerald-500 ${className}`} />;
    case 'running': return <PlayCircle size={size} className={`text-blue-500 animate-pulse ${className}`} />;
    case 'failed': return <AlertCircle size={size} className={`text-rose-500 ${className}`} />;
    case 'pending': return <Clock size={size} className={`text-amber-500 ${className}`} />;
    default: return <Clock size={size} className={`text-slate-400 ${className}`} />;
  }
}

export function TaskDetailPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const [task, setTask] = useState<TaskDetail | null>(null);
  const [childTasks, setChildTasks] = useState<TaskDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copying, setCopying] = useState(false);

  useEffect(() => {
    if (!taskId) return;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const detail = await getTaskDetail(taskId!);
        setTask(detail);
        // 加载子任务
        if (detail.child_task_ids?.length) {
          const children = await Promise.allSettled(
            detail.child_task_ids.map(id => getTaskDetail(id))
          );
          setChildTasks(
            children
              .filter((r): r is PromiseFulfilledResult<TaskDetail> => r.status === 'fulfilled')
              .map(r => r.value)
          );
        }
      } catch (e) {
        setError(e instanceof ApiError ? e.message : '加载任务详情失败');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [taskId]);

  const handleCopy = useCallback(async () => {
    if (!taskId) return;
    setCopying(true);
    try {
      const result = await copyTask(taskId);
      navigate(`/tasks/${result.new_task_id}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : '复制任务失败');
    } finally {
      setCopying(false);
    }
  }, [taskId, navigate]);

  // 基于该任务新建：将 input_data 回填为新建页草稿
  const handleRebuild = useCallback(() => {
    if (!task?.input_data) return;
    const data = task.input_data as Record<string, unknown>;
    const rawProductId = (data.product_id as string) || '';
    // _input_source 存储在 metadata 中，优先从 metadata 读取
    const meta = (task.metadata ?? {}) as Record<string, unknown>;
    const inputSource = (meta._input_source as string | undefined);

    // 区分"产品选择"和"手输主题"两种输入来源
    let productId = '';
    let customTopic = '';
    if (inputSource === 'custom_topic') {
      customTopic = rawProductId;
    } else if (inputSource === 'product') {
      productId = rawProductId;
    } else {
      // 旧任务无来源标记：保守回填到 customTopic，避免丢失手输内容
      customTopic = rawProductId;
    }

    const draft = {
      taskName: '',
      productId,
      customTopic,
      workflow: 'standard_chain' as const,
      audience: (data.audience as string) || '医学专业人士',
      projectName: (data.project_name as string) || '',
      targetWordCount: (data.target_word_count as number) || 2000,
      register: (data.register as string) || 'academic',
      notes: '',
    };
    localStorage.setItem('xiakedao_new_task_draft', JSON.stringify(draft));
    navigate('/tasks/new');
  }, [task, navigate]);

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12 flex justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12 text-center">
        <p className="text-red-600 mb-4">{error || '任务不存在'}</p>
        <Button variant="secondary" onClick={() => navigate('/')}>返回工作台</Button>
      </div>
    );
  }

  return (
    <div className="max-w-[1200px] mx-auto px-4 py-8 space-y-8 animate-in fade-in duration-300">
      {/* 导航面板 */}
      <div className="flex items-center justify-between">
        <div>
           <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
             <TerminalSquare size={22} className="text-brand-600" />
             任务执行详情
           </h2>
           <p className="text-xs text-slate-500 mt-1 ml-8">任务 ID: <span className="font-mono">{taskId}</span></p>
        </div>
        <Button variant="ghost" size="sm" onClick={() => navigate('/')} className="text-slate-500 hover:text-slate-900">
           <ArrowLeft size={16} className="mr-1.5" /> 返回工作台
        </Button>
      </div>

      {/* 核心入口区 (Launch Pad) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <button
          onClick={() => navigate(`/tasks/${taskId}/rewrite`)}
          className="group relative bg-white p-6 justify-start text-left border border-slate-200/80 rounded-2xl shadow-sm hover:shadow-md hover:border-brand-300 transition-all duration-300 overflow-hidden flex flex-col"
        >
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity"><Edit3 size={64} /></div>
          <div className="w-10 h-10 rounded-xl bg-brand-50 flex items-center justify-center text-brand-600 mb-4 group-hover:scale-110 transition-transform">
             <Edit3 size={20} />
          </div>
          <h3 className="text-base font-bold text-slate-800 mb-1">修改文章</h3>
          <p className="text-xs text-slate-500 font-medium">如果对生成的文章不满意，可以在这里按段落手动修改，或提供要求让 AI 重新改写。</p>
        </button>

        <button
          onClick={() => navigate(`/tasks/${taskId}/review`)}
          className="group relative bg-white p-6 justify-start text-left border border-slate-200/80 rounded-2xl shadow-sm hover:shadow-md hover:border-indigo-300 transition-all duration-300 overflow-hidden flex flex-col"
        >
           <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 text-indigo-900 transition-opacity"><Eye size={64} /></div>
           <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600 mb-4 group-hover:scale-110 transition-transform">
             <Eye size={20} />
          </div>
          <h3 className="text-base font-bold text-slate-800 mb-1">审阅与批注</h3>
          <p className="text-xs text-slate-500 font-medium">在这里可以总览全稿，添加具体的修改意见（批注），并决定文章是直接通过还是打回重修。</p>
        </button>

        <button
          onClick={() => navigate(`/tasks/${taskId}/compare`)}
          className="className=group relative bg-white p-6 justify-start text-left border border-slate-200/80 rounded-2xl shadow-sm hover:shadow-md hover:border-emerald-300 transition-all duration-300 overflow-hidden flex flex-col"
        >
           <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 text-emerald-900 transition-opacity"><GitCompare size={64} /></div>
           <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600 mb-4 group-hover:scale-110 transition-transform">
             <GitCompare size={20} />
          </div>
          <h3 className="text-base font-bold text-slate-800 mb-1">查看版本对比</h3>
          <p className="text-xs text-slate-500 font-medium">如果文章经历了多次修改，在这里可以清晰地对比新旧版本的字句差异，并决定是否采纳。</p>
        </button>
      </div>

      {/* 任务头卡 */}
      <Card className="shadow-sm border-slate-200/60 overflow-hidden">
        <CardBody className="p-0">
          <div className="flex flex-col md:flex-row md:items-stretch">
            <div className="p-6 md:w-2/3 border-b md:border-b-0 md:border-r border-slate-100 flex flex-col justify-center">
              <div className="flex items-center gap-3 mb-2">
                 <StatusIcon status={task.status} size={20} />
                <h2 className="text-lg font-bold text-slate-800 tracking-wide">
                   {CHAIN_STEP_LABELS[task.module] || task.module}
                </h2>
                <Badge variant={statusVariant(task.status)} size="md" className="shadow-sm">{task.status}</Badge>
              </div>
              <div className="flex gap-6 mt-4 text-xs text-slate-500 font-medium bg-slate-50/50 w-fit px-4 py-2 rounded-lg border border-slate-100">
                <span className="flex items-center gap-1.5"><Clock size={12}/>开始：{new Date(task.started_at).toLocaleString('zh-CN')}</span>
                {task.completed_at && (
                  <span className="flex items-center gap-1.5"><CheckCircle2 size={12}/>完成：{new Date(task.completed_at).toLocaleString('zh-CN')}</span>
                )}
                {task.duration_ms != null && (
                  <span className="flex items-center gap-1.5 text-slate-700 font-bold bg-white px-2 py-0.5 rounded shadow-sm border border-slate-200">耗时：{(task.duration_ms / 1000).toFixed(1)}s</span>
                )}
              </div>
            </div>
            <div className="p-6 md:w-1/3 flex flex-col justify-center gap-3 bg-slate-50/30">
               <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">快捷操作</h4>
              {task.input_data && (
                 <Button variant="primary" size="md" onClick={handleRebuild} className="w-full shadow-sm bg-brand-600 hover:bg-brand-700">
                   <Plus size={16} className="mr-2" /> 使用相同配置新建任务
                 </Button>
              )}
              <Button variant="secondary" size="md" className="w-full bg-white border-slate-200 hover:bg-slate-50 text-slate-700 border shadow-sm" onClick={handleCopy} disabled={copying}>
                 <Copy size={16} className="mr-2 text-slate-400" /> {copying ? '复制中...' : '复制一个相同的任务'}
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* 错误信息 */}
      {task.error_message && (
        <Card>
          <CardHeader>
            <h3 className="text-sm font-medium text-red-700">错误日志</h3>
          </CardHeader>
          <CardBody>
            <pre className="text-xs text-red-600 bg-red-50 p-3 rounded overflow-x-auto whitespace-pre-wrap">
              {task.error_message}
            </pre>
          </CardBody>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 输入数据 */}
        <Card className="shadow-sm border-slate-200/60 flex flex-col min-h-[300px]">
          <CardHeader className="py-3 px-5 bg-slate-50/80 border-b border-slate-100/80 shrink-0">
            <h3 className="text-xs font-bold font-mono text-slate-500 flex items-center gap-2"><FileJson size={14}/> 接口输入数据 (Input Payload)</h3>
          </CardHeader>
          <CardBody className="p-0 flex-1 relative bg-slate-900 text-slate-300">
            {task.input_data ? (
              <pre className="text-xs font-mono p-4 overflow-x-auto max-h-[400px] whitespace-pre-wrap shrink-0">
                {JSON.stringify(task.input_data, null, 2)}
              </pre>
            ) : (
              <div className="flex items-center justify-center absolute inset-0 text-slate-500 text-sm">空数据</div>
            )}
          </CardBody>
        </Card>

        {/* 输出数据 */}
        <Card className="shadow-sm border-slate-200/60 flex flex-col min-h-[300px]">
          <CardHeader className="py-3 px-5 bg-slate-50/80 border-b border-slate-100/80 shrink-0">
            <h3 className="text-xs font-bold font-mono text-slate-500 flex items-center gap-2"><FileJson size={14}/> 执行结果数据 (Output Payload)</h3>
          </CardHeader>
          <CardBody className="p-0 flex-1 relative bg-slate-900 text-slate-300">
            {task.output_data ? (
              <pre className="text-xs font-mono p-4 overflow-x-auto max-h-[400px] whitespace-pre-wrap shrink-0">
                {JSON.stringify(task.output_data, null, 2)}
              </pre>
            ) : (
              <div className="flex items-center justify-center absolute inset-0 text-slate-500 text-sm">暂无返回（执行中或失败）</div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* 子任务时间线 */}
      {childTasks.length > 0 && (
        <Card className="shadow-sm border-slate-200/60 overflow-hidden">
          <CardHeader className="py-3 px-5 bg-white border-b border-slate-100 shrink-0">
            <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2"><TerminalSquare size={16} className="text-indigo-500"/> 任务执行步骤记录</h3>
          </CardHeader>
          <CardBody className="p-0">
            <div className="divide-y divide-slate-100">
              {childTasks.map((child, i) => (
                <Link
                  key={child.task_id}
                  to={`/tasks/${child.task_id}`}
                  className="block px-6 py-4 hover:bg-slate-50 transition-colors group relative"
                >
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-transparent group-hover:bg-indigo-500 transition-colors"></div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="w-7 h-7 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center text-xs font-bold shadow-sm">
                        {i + 1}
                      </span>
                      <StatusIcon status={child.status} size={16} />
                      <span className="text-sm font-bold text-slate-700 tracking-wide">
                        {CHAIN_STEP_LABELS[child.module] || child.module}
                      </span>
                      <Badge variant={statusVariant(child.status)} size="sm" className="ml-1 shadow-sm font-mono">
                        {child.status}
                      </Badge>
                    </div>
                    <span className="text-xs text-slate-400 font-mono bg-white px-2 py-1 rounded border border-slate-200 shadow-sm">
                      {child.duration_ms != null ? `${(child.duration_ms / 1000).toFixed(1)}s` : '—'}
                    </span>
                  </div>
                  {child.error_message && (
                    <div className="ml-10 mt-2 p-2 bg-rose-50 border border-rose-100 rounded text-xs text-rose-600 font-medium">
                        <AlertCircle size={12} className="inline mr-1" />{child.error_message}
                    </div>
                  )}
                </Link>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* 元数据 */}
      {task.metadata && Object.keys(task.metadata).length > 0 && (
        <Card>
          <CardHeader>
            <h3 className="text-sm font-medium text-gray-900">元数据</h3>
          </CardHeader>
          <CardBody>
            <pre className="text-xs text-gray-700 bg-gray-50 p-3 rounded overflow-x-auto max-h-40 whitespace-pre-wrap">
              {JSON.stringify(task.metadata, null, 2)}
            </pre>
          </CardBody>
        </Card>
      )}
    </div>
  );
}
