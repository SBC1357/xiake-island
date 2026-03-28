/**
 * Dashboard Page — 工作台首页
 * 
 * 最近任务 + 最近交付 + 待继续任务 + 知识资产摘要 + 快速新建入口
 */

import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody, CardFooter, Button, Badge, Spinner } from '../components/ui';
import { listTasks, type TaskListItem } from '../api/tasks';
import { getDeliveryHistory, type DeliveryHistoryItem } from '../api/delivery';
import { getKnowledgeAssets, type KnowledgeAssetsResponse } from '../api/workflow';
import { getEvidenceStats, type EvidenceStatsResponse } from '../api/evidence';
import { Plus, FileText, Clock, Archive, ArrowRight, CheckCircle2, AlertCircle, Loader2, Send, Library, Database } from 'lucide-react';

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

type TaskStatus = '草稿中' | '运行中' | '质量待处理' | '待改稿' | '已交付';

function mapTaskStatus(status: string): TaskStatus {
  switch (status) {
    case 'completed': return '已交付';
    case 'running': return '运行中';
    case 'failed': return '质量待处理';
    case 'pending': return '草稿中';
    default: return '草稿中';
  }
}

function statusBadgeVariant(status: TaskStatus): 'success' | 'warning' | 'danger' | 'info' | 'default' {
  switch (status) {
    case '已交付': return 'success';
    case '运行中': return 'info';
    case '质量待处理': return 'warning';
    case '待改稿': return 'warning';
    case '草稿中': return 'default';
  }
}

function StatusIcon({ status }: { status: TaskStatus }) {
  switch (status) {
    case '已交付': return <CheckCircle2 size={16} className="text-emerald-500" />;
    case '运行中': return <Loader2 size={16} className="text-blue-500 animate-spin" />;
    case '质量待处理': return <AlertCircle size={16} className="text-amber-500" />;
    case '待改稿': return <AlertCircle size={16} className="text-amber-500" />;
    case '草稿中': return <Clock size={16} className="text-slate-400" />;
  }
}

export function DashboardPage() {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<TaskListItem[]>([]);
  const [deliveryItems, setDeliveryItems] = useState<DeliveryHistoryItem[]>([]);
  const [knowledgeAssets, setKnowledgeAssets] = useState<KnowledgeAssetsResponse | null>(null);
  const [evidenceStats, setEvidenceStats] = useState<EvidenceStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [taskRes, deliveryRes, assetsRes, statsRes] = await Promise.allSettled([
          listTasks({ limit: 15 }),
          getDeliveryHistory(),
          getKnowledgeAssets(),
          getEvidenceStats(),
        ]);
        if (taskRes.status === 'fulfilled') setTasks(taskRes.value.tasks);
        if (deliveryRes.status === 'fulfilled') setDeliveryItems(deliveryRes.value.items.slice(0, 5));
        if (assetsRes.status === 'fulfilled') setKnowledgeAssets(assetsRes.value);
        if (statsRes.status === 'fulfilled') setEvidenceStats(statsRes.value);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const pendingTasks = tasks.filter(t => t.status !== 'completed' && t.status !== 'failed');

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[50vh] text-slate-400 gap-4">
        <Spinner size="lg" />
        <p className="text-sm font-medium animate-pulse">加载工作台数据...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header Area */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">早安，编辑部</h2>
          <p className="text-slate-500 mt-1.5 text-sm">此视图汇总了您最近创建的自动化写作流程和执行结果。</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Button variant="secondary" onClick={() => navigate('/workflow/article')}>
            <FileText size={16} />
            文章工作流
          </Button>
          <Button onClick={() => navigate('/tasks/new')}>
            <Plus size={16} />
            新建写作任务
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Left: Main tasks tracking */}
        <div className="xl:col-span-2 space-y-8">
          
          {/* Action-needed tasks */}
          {pendingTasks.length > 0 && (
            <Card>
              <CardHeader className="bg-amber-50/30 border-b border-amber-100/50">
                <div className="flex items-center justify-between w-full">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.6)]"></div>
                    <h3 className="text-sm font-semibold text-slate-800">进行中任务</h3>
                  </div>
                  <Badge variant="warning">{pendingTasks.length} 项</Badge>
                </div>
              </CardHeader>
              <CardBody className="p-0">
                <div className="divide-y divide-slate-100">
                  {pendingTasks.slice(0, 5).map(task => {
                    const uiStatus = mapTaskStatus(task.status);
                    return (
                      <Link
                        key={task.task_id}
                        to={`/tasks/${task.task_id}`}
                        className="group flex flex-col sm:flex-row sm:items-center px-6 py-4 hover:bg-slate-50 transition-colors gap-4"
                      >
                        <div className="flex-shrink-0 mt-0.5 sm:mt-0">
                          <StatusIcon status={uiStatus} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-sm font-bold text-slate-900 truncate">
                              {CHAIN_STEP_LABELS[task.module] || task.module}
                            </span>
                            <Badge variant={statusBadgeVariant(uiStatus)} size="sm">
                              {uiStatus}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-3 text-xs text-slate-500">
                            <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">
                              {task.task_id.slice(0, 8)}
                            </span>
                            <span>{new Date(task.started_at).toLocaleString('zh-CN')}</span>
                          </div>
                        </div>
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button variant="secondary" size="sm" className="bg-white">
                            进入控制台 <ArrowRight size={14} />
                          </Button>
                        </div>
                      </Link>
                    );
                  })}
                </div>
              </CardBody>
            </Card>
          )}

          {/* All recent tasks */}
          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold text-slate-800">最近任务记录</h3>
            </CardHeader>
            <CardBody className="p-0">
              {tasks.length === 0 ? (
                <div className="px-6 py-12 text-center text-sm text-slate-500 flex flex-col items-center">
                  <div className="w-12 h-12 bg-slate-100 flex items-center justify-center rounded-full mb-3 text-slate-400">
                    <FileText size={20} />
                  </div>
                  <p>工作台目前空空如也，</p>
                  <Link to="/tasks/new" className="text-brand-600 font-medium hover:underline mt-1">
                    点击这里创建您的第一个写作任务
                  </Link>
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {tasks.slice(0, 10).map(task => {
                    const uiStatus = mapTaskStatus(task.status);
                    const isError = task.status === 'failed';
                    return (
                      <Link
                        key={task.task_id}
                        to={`/tasks/${task.task_id}`}
                        className="flex flex-col sm:flex-row sm:items-center px-6 py-4 hover:bg-slate-50 transition-all gap-4 group"
                      >
                         <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-sm font-medium text-slate-900 truncate">{CHAIN_STEP_LABELS[task.module] || task.module}</span>
                            <Badge variant={statusBadgeVariant(uiStatus)} size="sm">{uiStatus}</Badge>
                          </div>
                          <div className="flex items-center gap-3 text-xs text-slate-500">
                            <span className="font-mono text-slate-400">{task.task_id.slice(0, 8)}</span>
                            <span>{new Date(task.started_at).toLocaleString('zh-CN')}</span>
                            {task.duration_ms && (
                              <span className="flex items-center gap-1">
                                <Clock size={12} /> {(task.duration_ms / 1000).toFixed(1)}s
                              </span>
                            )}
                          </div>
                          {isError && task.error_message && (
                            <p className="text-xs text-red-500 mt-2 bg-red-50 px-2 py-1 rounded truncate border border-red-100">
                              {task.error_message}
                            </p>
                          )}
                        </div>
                        <div className="sm:opacity-0 group-hover:opacity-100 transition-opacity text-slate-400">
                           <ArrowRight size={18} />
                        </div>
                      </Link>
                    );
                  })}
                </div>
              )}
            </CardBody>
          </Card>
        </div>

        {/* Right: Knowledge Assets & Deliveries Sidebar */}
        <div className="space-y-6">
          
          <Card className="bg-slate-900 border-none text-slate-100 overflow-hidden relative shadow-lg">
            <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
              <Library size={100} />
            </div>
            <CardHeader className="border-slate-800">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <Archive size={16} className="text-brand-400" />
                资产引擎状态
              </h3>
            </CardHeader>
            <CardBody className="relative z-10 p-5">
              {knowledgeAssets ? (
                <div className="space-y-4 text-sm">
                  <div className="flex justify-between items-center pb-3 border-b border-slate-800">
                    <span className="text-slate-400">受众人群设定预设</span>
                    <span className="font-mono text-lg font-medium text-brand-300">{knowledgeAssets.consumer_assets_count}</span>
                  </div>
                  <div className="flex justify-between items-center pb-3 border-b border-slate-800">
                    <span className="text-slate-400">文章审核规则预设</span>
                    <span className="font-mono text-lg font-medium text-brand-300">{knowledgeAssets.rules_assets_count}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">高级调度引擎支撑</span>
                    <Badge variant={knowledgeAssets.has_l2 ? 'success' : 'warning'} className={knowledgeAssets.has_l2 ? 'bg-emerald-500/20 text-emerald-300 border-0' : 'bg-amber-500/20 text-amber-300 border-0'}>
                      {knowledgeAssets.has_l2 ? '运行中' : '未就绪'}
                    </Badge>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-sm text-slate-500 py-4">
                  <AlertCircle size={16} /> 无法连接资产库
                </div>
              )}
            </CardBody>
            <CardFooter className="bg-slate-950/50 border-t border-slate-800">
              <Link
                to="/knowledge-assets"
                className="text-xs font-medium text-brand-400 hover:text-brand-300 hover:underline flex items-center gap-1 w-full justify-between group"
              >
                管理并查看系统运行资产库
                <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
              </Link>
            </CardFooter>
          </Card>

          {/* Evidence Stats Card */}
          {evidenceStats && (
            <Card>
              <CardHeader>
                <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
                  <Database size={16} className="text-blue-500" />
                  证据数据统计
                </h3>
              </CardHeader>
              <CardBody className="space-y-3">
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div>
                    <p className="text-xl font-bold text-blue-600">{evidenceStats.total_facts}</p>
                    <p className="text-xs text-slate-500">事实条目</p>
                  </div>
                  <div>
                    <p className="text-xl font-bold text-emerald-600">{evidenceStats.total_sources}</p>
                    <p className="text-xs text-slate-500">来源文献</p>
                  </div>
                  <div>
                    <p className="text-xl font-bold text-purple-600">{evidenceStats.total_products}</p>
                    <p className="text-xs text-slate-500">产品覆盖</p>
                  </div>
                </div>
                {Object.keys(evidenceStats.source_type_distribution).length > 0 && (
                  <div className="pt-2 border-t border-slate-100">
                    <p className="text-xs text-slate-500 mb-2">来源类型分布</p>
                    <div className="flex flex-wrap gap-1.5">
                      {Object.entries(evidenceStats.source_type_distribution).map(([type, count]) => (
                        <Badge key={type} variant="default" size="sm">
                          {type}: {count}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardBody>
            </Card>
          )}

          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
                <Send size={16} className="text-slate-400" />
                最新交付文件
              </h3>
            </CardHeader>
            <CardBody className="p-0">
              {deliveryItems.length === 0 ? (
                <div className="px-5 py-8 text-center text-sm text-slate-500">
                  暂无交付记录
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {deliveryItems.map((item, i) => (
                    <div key={i} className="px-5 py-3 hover:bg-slate-50 transition-colors group">
                      <p className="text-sm font-medium text-slate-700 truncate group-hover:text-brand-600 transition-colors">{item.filename}</p>
                      {item.created_at && (
                        <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                          <CheckCircle2 size={12} className="text-emerald-500" />
                          {new Date(item.created_at).toLocaleString('zh-CN')}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardBody>
            <CardFooter>
              <Link to="/delivery" className="text-xs font-medium text-brand-600 hover:underline w-full text-center">
                查看全部中心文件 →
              </Link>
            </CardFooter>
          </Card>

        </div>
      </div>
    </div>
  );
}
