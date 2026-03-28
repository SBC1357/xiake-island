/**
 * App Layout — 全局导航布局
 */

import { NavLink, Outlet } from 'react-router-dom';
import { Home, Send, Library, ArrowLeftSquare, PenTool, FileText, ClipboardCheck } from 'lucide-react';

const NAV_ITEMS = [
  { to: '/', label: '工作台', icon: Home, end: true },
  { to: '/tasks/new', label: '新建任务', icon: PenTool },
  { to: '/workflow/article', label: '文章工作流', icon: FileText },
  { to: '/review/independent', label: '独立审改', icon: ClipboardCheck },
  { to: '/delivery', label: '交付中心', icon: Send },
  { to: '/knowledge-assets', label: '知识资产', icon: Library },
];

const SECONDARY_NAV_ITEMS = [
  { to: '/legacy', label: '旧版入口', icon: ArrowLeftSquare, end: false },
];

export function AppLayout() {
  return (
    <div className="flex h-screen bg-slate-50 text-slate-800 font-sans overflow-hidden">
      {/* 侧边栏 */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shadow-xl z-20 sticky top-0 h-screen">
        <div className="h-16 flex items-center px-6 border-b border-slate-800 bg-slate-950">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center mr-3 shadow-sm shadow-brand-500/50">
            <PenTool size={18} className="text-white" />
          </div>
          <span className="text-lg font-bold text-slate-50 tracking-wide">
            侠客岛 <span className="text-brand-400 font-medium text-sm ml-1">v2</span>
          </span>
        </div>

        <div className="flex-1 py-6 px-4 flex flex-col gap-1 overflow-y-auto">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">主导航</div>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-brand-600 text-white shadow-md shadow-brand-600/20'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'
                }`
              }
            >
              <item.icon size={18} />
              <span className="text-sm font-medium">{item.label}</span>
            </NavLink>
          ))}
          
          <div className="mt-8 mb-2 px-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">系统及其他</div>
          {SECONDARY_NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-slate-800 text-slate-100'
                    : 'text-slate-500 hover:bg-slate-800/50 hover:text-slate-300'
                }`
              }
            >
              <item.icon size={18} />
              <span className="text-sm font-medium">{item.label}</span>
            </NavLink>
          ))}
        </div>
        
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-slate-800/50">
            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-slate-300 font-bold text-sm">
              ED
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-200 truncate">编辑部</p>
              <p className="text-xs text-slate-500 truncate">当前工作区</p>
            </div>
          </div>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center px-8 shadow-sm z-10 shrink-0">
          <h1 className="text-lg font-semibold text-slate-800">编辑工作台</h1>
          <div className="ml-auto flex items-center gap-4">
            <div className="text-sm text-slate-500 bg-slate-100 px-3 py-1.5 rounded-full border border-slate-200 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              系统运行中
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto bg-slate-50 relative p-8">
          <div className="max-w-6xl mx-auto pb-12 w-full">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
}
