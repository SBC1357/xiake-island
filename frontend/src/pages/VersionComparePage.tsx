/**
 * Version Compare Page — 版本对比页
 *
 * 版本选择器 + 双栏 diff 视图 + 锁定段落警告 + 改稿元数据摘要
 * 阶段口径：后端契约已定义，前端联调已接线
 */

import { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody, Button, Select, Badge, Spinner } from '../components/ui';
import { GitCompare, ArrowLeft, GitCommit, Link as LinkIcon, AlertTriangle, PlusCircle, MinusCircle, Edit2, PlayCircle, RotateCcw, PenTool } from 'lucide-react';
import { getTaskDetail, type TaskDetail } from '../api/tasks';
import {
  getVersionList,
  compareVersions,
  acceptVersion,
  type VersionMeta,
  type VersionCompareResponse,
} from '../api/versions';
import { ApiError } from '../api/client';

// ============ Helper ============

function diffColor(status: string) {
  switch (status) {
    case 'added': return 'bg-emerald-50/60 border-emerald-200 shadow-[inset_4px_0_0_0_#34d399]';
    case 'removed': return 'bg-rose-50/60 border-rose-200 shadow-[inset_4px_0_0_0_#fb7185] opacity-75 grayscale-[0.2]';
    case 'modified': return 'bg-amber-50/60 border-amber-200 shadow-[inset_4px_0_0_0_#fbbf24]';
    default: return 'bg-white border-slate-200 hover:border-slate-300 transition-colors shadow-sm';
  }
}

function diffBadge(status: string) {
  switch (status) {
    case 'added': return <Badge variant="success" size="sm" className="bg-emerald-100 text-emerald-700 border-emerald-200/50"><PlusCircle size={10} className="mr-1 inline" />新增</Badge>;
    case 'removed': return <Badge variant="danger" size="sm" className="bg-rose-100 text-rose-700 border-rose-200/50"><MinusCircle size={10} className="mr-1 inline" />删除</Badge>;
    case 'modified': return <Badge variant="warning" size="sm" className="bg-amber-100 text-amber-700 border-amber-200/50"><Edit2 size={10} className="mr-1 inline" />修改</Badge>;
    default: return null;
  }
}

// ============ 组件 ============

export function VersionComparePage() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();

  // 数据加载
  const [task, setTask] = useState<TaskDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [versions, setVersions] = useState<VersionMeta[]>([]);
  const [versionsLoading, setVersionsLoading] = useState(false);

  // 版本选择
  const [leftVersion, setLeftVersion] = useState('');
  const [rightVersion, setRightVersion] = useState('');

  // 对比结果
  const [compareResult, setCompareResult] = useState<VersionCompareResponse | null>(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState<string | null>(null);

  // 操作
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const versionOptions = useMemo(() =>
    versions.map(v => ({
      value: v.version,
      label: `${v.version} — ${v.label}（${new Date(v.created_at).toLocaleString('zh-CN')}）`,
    })),
    [versions],
  );

  const leftMeta = useMemo(() => versions.find(v => v.version === leftVersion), [versions, leftVersion]);
  const rightMeta = useMemo(() => versions.find(v => v.version === rightVersion), [versions, rightVersion]);

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

  // 加载版本列表
  useEffect(() => {
    if (!task?.input_hash) return;
    setVersionsLoading(true);
    getVersionList(task.input_hash)
      .then(res => {
        setVersions(res.versions);
        // 默认选最后两个版本
        if (res.versions.length >= 2) {
          setLeftVersion(res.versions[res.versions.length - 2].version);
          setRightVersion(res.versions[res.versions.length - 1].version);
        } else if (res.versions.length === 1) {
          setLeftVersion(res.versions[0].version);
          setRightVersion(res.versions[0].version);
        }
      })
      .catch(() => setVersions([]))
      .finally(() => setVersionsLoading(false));
  }, [task?.input_hash]);

  // 加载对比结果
  useEffect(() => {
    if (!taskId || !leftVersion || !rightVersion) return;
    setCompareLoading(true);
    setCompareError(null);
    compareVersions(taskId, leftVersion, rightVersion)
      .then(res => setCompareResult(res))
      .catch(e => {
        setCompareError(e instanceof ApiError ? e.message : '加载对比数据失败');
        setCompareResult(null);
      })
      .finally(() => setCompareLoading(false));
  }, [taskId, leftVersion, rightVersion]);

  const handleAction = useCallback(async (action: 'accept' | 'rollback') => {
    if (!taskId) return;
    const version = action === 'accept' ? rightVersion : leftVersion;
    if (!version) return;
    setActionLoading(true);
    setActionError(null);
    setActionSuccess(null);
    try {
      await acceptVersion({ task_id: taskId, version, action });
      setActionSuccess(action === 'accept' ? `已接受版本 ${version}` : `已回滚到版本 ${version}`);
    } catch (e) {
      setActionError(e instanceof ApiError ? e.message : '操作失败');
    } finally {
      setActionLoading(false);
    }
  }, [taskId, leftVersion, rightVersion]);

  const lockedModified = useMemo(() =>
    compareResult?.paragraphs.filter(d => d.locked && d.status !== 'unchanged') ?? [],
    [compareResult],
  );

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
             <GitCompare size={20} className="text-brand-600" />
             版本对比
           </h2>
           <p className="text-xs text-slate-500 mt-1 ml-7">对比修改前后带来的具体差异</p>
        </div>
        <Button variant="ghost" size="sm" onClick={() => navigate(taskId ? `/tasks/${taskId}` : '/')} className="text-slate-500 hover:text-slate-900">
           <ArrowLeft size={16} className="mr-1.5" /> 返回任务详情
        </Button>
      </div>

      {/* 版本选择器 */}
      <Card className="mb-4 shrink-0 shadow-sm border-slate-200/60 overflow-visible">
        <CardBody className="p-4 bg-slate-50/30">
          {versionsLoading ? (
            <div className="flex justify-center py-4"><Spinner size="sm" /></div>
          ) : versions.length === 0 ? (
            <p className="text-sm text-slate-400 text-center font-medium">系统内暂无演化版次记录，请先触发改写管线</p>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-end relative">
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-white border border-slate-200 shadow-sm flex items-center justify-center z-10 hidden md:flex">
                   <LinkIcon size={14} className="text-slate-400 rotate-45" />
                </div>
                <Select
                  label="左侧版本"
                  value={leftVersion}
                  onChange={e => setLeftVersion(e.target.value)}
                  options={versionOptions}
                />
                <Select
                  label="右侧版本"
                  value={rightVersion}
                  onChange={e => setRightVersion(e.target.value)}
                  options={versionOptions}
                />
              </div>
              {leftMeta && rightMeta && (
                <div className="flex gap-8 mt-5 pt-4 border-t border-slate-100 text-sm font-medium text-slate-600 justify-center">
                  <span className="flex items-center gap-1.5"><GitCommit size={14} className="text-slate-400" />左栏：{leftMeta.word_count} tokens</span>
                  <span className="flex items-center gap-1.5"><GitCommit size={14} className="text-brand-400" />右栏：{rightMeta.word_count} tokens</span>
                  <span className="flex items-center gap-1.5 rounded-full px-3 bg-slate-100 text-slate-700">计算增量： <span className={`${rightMeta.word_count - leftMeta.word_count > 0 ? 'text-emerald-600' : rightMeta.word_count - leftMeta.word_count < 0 ? 'text-rose-600' : ''}`}>{rightMeta.word_count - leftMeta.word_count > 0 ? '+' : ''}{rightMeta.word_count - leftMeta.word_count}</span></span>
                </div>
              )}
            </>
          )}
        </CardBody>
      </Card>

      {/* 锁定段落警告 */}
      {lockedModified.length > 0 && (
        <div className="mb-4 p-4 bg-rose-50 border border-rose-200 rounded-lg flex gap-3 shadow-sm shrink-0">
          <AlertTriangle className="text-rose-500 shrink-0 mt-0.5" size={18} />
          <div>
            <p className="text-sm text-rose-800 font-bold mb-1">文章修改约束警告：系统检测到“已锁定设定”的段落被改了</p>
            <ul className="text-xs text-rose-600 space-y-0.5 font-mono list-disc ml-4">
              {lockedModified.map(d => (
                <li key={d.paragraph_id}>段落ID: <span className="font-semibold">{d.paragraph_id}</span> 内容发生了意外变更。</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* 对比加载/错误 */}
      {compareLoading && (
        <div className="flex justify-center py-12 flex-1 items-center"><Spinner size="lg" /></div>
      )}

      {compareError && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 shrink-0">
          <AlertTriangle size={16} className="text-red-500"/>
          <p className="text-sm text-red-700 font-medium">{compareError}</p>
        </div>
      )}

      {/* 双栏 Diff 视图 */}
      {compareResult && !compareLoading && (
        <div className="flex flex-col flex-1 min-h-0">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6 flex-1 min-h-0">
            {/* 左栏：旧版本 */}
            <Card className="flex flex-col shadow-sm border-slate-200/60 overflow-hidden">
              <CardHeader className="py-3 px-5 bg-slate-50/80 border-b border-slate-100/80 shrink-0">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold font-mono text-slate-500 flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-slate-300"></div> {leftVersion}</h3>
                  {leftMeta && <span className="text-xs font-medium text-slate-400">{new Date(leftMeta.created_at).toLocaleString('zh-CN')}</span>}
                </div>
              </CardHeader>
              <CardBody className="p-4 space-y-4 overflow-y-auto bg-slate-50/20 flex-1">
                {compareResult.paragraphs.filter(d => d.status !== 'added').map((d, i) => (
                  <div key={d.paragraph_id} className={`p-4 rounded-xl border text-sm transition-all duration-200 ${d.status === 'removed' ? 'bg-rose-50/50 border-rose-200 line-through decoration-rose-300 decoration-2' : d.status === 'modified' ? 'bg-amber-50/50 border-amber-200' : 'bg-white border-slate-200 shadow-sm'}`}>
                    <div className="flex items-center gap-2 mb-2">
                       <span className="text-xs text-slate-400 font-mono bg-slate-100 px-1.5 py-0.5 rounded">§{i + 1}</span>
                       <span className="text-xs text-slate-300 font-mono select-all ml-1">{d.paragraph_id}</span>
                      {d.locked && <Badge variant="warning" size="sm" className="ml-2 shadow-sm bg-amber-100 text-amber-700 border-amber-200/50">🔒 Protected</Badge>}
                      <div className="ml-auto">{diffBadge(d.status)}</div>
                    </div>
                    <p className="text-slate-600 leading-relaxed font-serif">{d.old_text}</p>
                  </div>
                ))}
              </CardBody>
            </Card>

            {/* 右栏：新版本 */}
            <Card className="flex flex-col shadow-sm border-brand-200/60 overflow-hidden relative group">
              <div className="absolute top-0 left-0 w-full h-1 bg-brand-500/80 z-10 relative"></div>
              <CardHeader className="py-2.5 px-5 bg-brand-50/40 border-b border-brand-100/60 shrink-0">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold font-mono text-brand-700 flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-brand-500 animate-pulse"></div> {rightVersion}</h3>
                  {rightMeta && <span className="text-xs font-medium text-brand-600/60">{new Date(rightMeta.created_at).toLocaleString('zh-CN')}</span>}
                </div>
              </CardHeader>
              <CardBody className="p-4 space-y-4 overflow-y-auto bg-white flex-1 relative">
                 <div className="absolute inset-x-0 top-0 h-4 bg-gradient-to-b from-white to-transparent z-10 pointer-events-none hidden group-hover:block" />
                {compareResult.paragraphs.filter(d => d.status !== 'removed').map((d, i) => (
                  <div key={d.paragraph_id} className={`p-5 rounded-xl border text-sm transition-all duration-300 ${diffColor(d.status)}`}>
                    <div className="flex items-center gap-2 mb-3">
                       <span className="text-xs text-slate-500 font-mono bg-slate-100/80 px-1.5 py-0.5 rounded">§{i + 1}</span>
                      {d.locked && <Badge variant="warning" size="sm" className="ml-2 shadow-sm">🔒 Protected</Badge>}
                      {d.locked && d.status !== 'unchanged' && (
                        <Badge variant="danger" size="sm" className="ml-1 shadow-sm font-bold border border-rose-300">越权违规</Badge>
                      )}
                      <div className="ml-auto flex items-center gap-2">
                        {d.status !== 'unchanged' && <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Patch Delta</span>}
                        {diffBadge(d.status)}
                      </div>
                    </div>
                    <p className="text-slate-800 leading-relaxed font-serif">{d.new_text}</p>
                  </div>
                ))}
              </CardBody>
            </Card>
          </div>

          {/* 改稿元数据摘要 + 操作区 */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm shrink-0">
            <div className="lg:col-span-8 flex flex-col justify-center space-y-3">
               <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2 mb-1">
                 <GitCommit size={16} className="text-indigo-500"/> 计算摘要元数据快照
               </h3>
               <div className="flex flex-wrap gap-4 text-sm font-medium">
                  <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
                    <span className="text-slate-500">解析模式:</span>
                    <Badge variant="info" size="md" className="font-mono">{compareResult.metadata.mode}</Badge>
                  </div>
                  <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
                    <span className="text-slate-500">实体密度守恒率:</span>
                    <Badge variant="success" size="md">{compareResult.metadata.conservation_status}</Badge>
                  </div>
               </div>
               {(compareResult.metadata.added_points.length > 0 || compareResult.metadata.removed_points.length > 0) && (
                 <div className="grid grid-cols-2 gap-4 mt-2">
                    {compareResult.metadata.added_points.length > 0 && (
                      <div className="bg-emerald-50/50 p-3 rounded-lg border border-emerald-100/50">
                        <p className="text-xs font-bold text-emerald-700 mb-1.5 flex items-center gap-1"><PlusCircle size={12}/> 增投探测点</p>
                        <ul className="text-xs text-emerald-800 space-y-1 font-mono">
                          {compareResult.metadata.added_points.map((p, i) => <li key={i} className="truncate" title={p}>+ {p}</li>)}
                        </ul>
                      </div>
                    )}
                    {compareResult.metadata.removed_points.length > 0 && (
                      <div className="bg-rose-50/50 p-3 rounded-lg border border-rose-100/50">
                        <p className="text-xs font-bold text-rose-700 mb-1.5 flex items-center gap-1"><MinusCircle size={12}/> 遗失判定区</p>
                        <ul className="text-xs text-rose-800 space-y-1 font-mono">
                          {compareResult.metadata.removed_points.map((p, i) => <li key={i} className="truncate" title={p}>− {p}</li>)}
                        </ul>
                      </div>
                    )}
                 </div>
               )}
            </div>

            <div className="lg:col-span-4 pl-0 lg:pl-6 border-t lg:border-t-0 lg:border-l border-slate-100 pt-4 lg:pt-0 flex flex-col justify-center space-y-2.5">
               {actionSuccess && <p className="text-xs font-medium text-emerald-600 bg-emerald-50 px-3 py-2 rounded-lg border border-emerald-100 mb-1">{actionSuccess}</p>}
               {actionError && <p className="text-xs font-medium text-rose-600 bg-rose-50 px-3 py-2 rounded-lg border border-rose-100 mb-1">{actionError}</p>}
               
               <Button
                  className="w-full shadow-sm h-11"
                  variant="primary"
                  disabled={actionLoading || !rightVersion}
                  onClick={() => handleAction('accept')}
                >
                  {actionLoading ? <><Spinner size="sm" className="mr-2 text-white" /> 写入树中...</> : <><PlayCircle size={16} className="mr-2" /> 将此变体并入主轨 (Accept)</>}
                </Button>
                <Button
                  className="w-full bg-white text-slate-700 border-slate-300 hover:bg-slate-50 hover:text-slate-900 border-2 shadow-sm h-11"
                  variant="secondary"
                  disabled={actionLoading || !leftVersion}
                  onClick={() => handleAction('rollback')}
                >
                  <RotateCcw size={16} className="mr-2" /> 对齐并退回基准支系
                </Button>
                <div className="my-1.5 flex items-center justify-center -space-x-1 opacity-60 pointer-events-none">
                   <div className="w-1.5 h-1.5 rounded-full bg-slate-300"></div><div className="w-1.5 h-1.5 rounded-full bg-slate-300"></div><div className="w-1.5 h-1.5 rounded-full bg-slate-300"></div>
                </div>
                <Button className="w-full text-brand-700 bg-brand-50 hover:bg-brand-100 border border-brand-200 h-10" variant="secondary" onClick={() => navigate(taskId ? `/tasks/${taskId}/rewrite` : '/')}>
                  <PenTool size={14} className="mr-2" /> 转入高级改写控制台
                </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
