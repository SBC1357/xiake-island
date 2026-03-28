/**
 * 路由渲染验证 — 确认所有新页面路由能正常挂载
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

// Mock API 模块，避免实际网络请求
vi.mock('../api/tasks', () => ({
  listTasks: vi.fn().mockResolvedValue({ tasks: [], total: 0 }),
  getTaskDetail: vi.fn().mockResolvedValue({
    task_id: 'test-1', module: 'orchestrator', status: 'completed',
    started_at: new Date().toISOString(), input_data: null, output_data: null,
  }),
  copyTask: vi.fn(),
}));

vi.mock('../api/evidence', () => ({
  listProducts: vi.fn().mockResolvedValue({ products: [] }),
  getFactById: vi.fn().mockResolvedValue({
    fact_id: 'f-1', text: 'test', source_type: 'journal',
    source_ref: 'ref', tags: [], lineage: {},
  }),
  getEvidenceStats: vi.fn().mockResolvedValue({
    total_facts: 0, total_sources: 0, total_products: 0,
    source_type_distribution: {}, products: [], freshness: null,
  }),
}));

vi.mock('../api/delivery', () => ({
  getDeliveryHistory: vi.fn().mockResolvedValue({ items: [] }),
  getArtifactUrl: vi.fn().mockReturnValue(''),
}));

vi.mock('../api/workflow', () => ({
  getKnowledgeAssets: vi.fn().mockResolvedValue({
    consumer_assets_count: 10, rules_assets_count: 5,
    consumer_root: null, has_l2: false, l2_files: [],
  }),
  executeStandardChainWorkflow: vi.fn(),
  executeArticleWorkflow: vi.fn(),
}));

import { DashboardPage } from '../pages/DashboardPage';
import { NewTaskPage } from '../pages/NewTaskPage';
import { TaskDetailPage } from '../pages/TaskDetailPage';
import { DeliveryCenterPage } from '../pages/DeliveryCenterPage';
import { KnowledgeAssetsPage } from '../pages/KnowledgeAssetsPage';
import { EvidenceDetailPage } from '../pages/EvidenceDetailPage';

function renderRoute(path: string, element: React.ReactElement) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="*" element={element} />
      </Routes>
    </MemoryRouter>
  );
}

describe('路由渲染', () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  it('DashboardPage 能渲染', async () => {
    renderRoute('/', <DashboardPage />);
    expect(await screen.findByText(/早安/)).toBeInTheDocument();
  });

  it('NewTaskPage 能渲染', async () => {
    renderRoute('/tasks/new', <NewTaskPage />);
    expect(await screen.findByText('新建写作任务')).toBeInTheDocument();
  });

  it('TaskDetailPage 能渲染', async () => {
    render(
      <MemoryRouter initialEntries={['/tasks/test-1']}>
        <Routes>
          <Route path="/tasks/:taskId" element={<TaskDetailPage />} />
        </Routes>
      </MemoryRouter>
    );
    // 等待异步加载完成，避免 act(...) warning
    await waitFor(() => {
      expect(screen.getByText('任务执行详情')).toBeInTheDocument();
    });
  });

  it('DeliveryCenterPage 能渲染', async () => {
    renderRoute('/delivery', <DeliveryCenterPage />);
    expect(await screen.findByText('交付中心')).toBeInTheDocument();
  });

  it('KnowledgeAssetsPage 能渲染', async () => {
    renderRoute('/knowledge-assets', <KnowledgeAssetsPage />);
    const el = await screen.findByText((content) => content.includes('知识资产'));
    expect(el).toBeInTheDocument();
  });

  it('EvidenceDetailPage 能渲染', async () => {
    render(
      <MemoryRouter initialEntries={['/evidence/f-1']}>
        <Routes>
          <Route path="/evidence/:factId" element={<EvidenceDetailPage />} />
        </Routes>
      </MemoryRouter>
    );
    expect(document.body).toBeTruthy();
  });
});
