/**
 * TaskDetailPage 交互验证
 * - 历史任务重建：product / custom_topic / legacy fallback 三路径
 * - 条件项入口：改稿 / 提交审阅 / 版本对比 按钮存在及跳转
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import type { TaskDetail } from '../api/tasks';

// --- Mocks ---

const mockGetTaskDetail = vi.fn<(id: string) => Promise<TaskDetail>>();

vi.mock('../api/tasks', () => ({
  getTaskDetail: (...args: unknown[]) => mockGetTaskDetail(args[0] as string),
  copyTask: vi.fn().mockResolvedValue({ new_task_id: 'copy-1' }),
}));

vi.mock('../api/delivery', () => ({
  getDeliveryHistory: vi.fn().mockResolvedValue({ items: [] }),
  getArtifactUrl: vi.fn().mockReturnValue(''),
}));

import { TaskDetailPage } from '../pages/TaskDetailPage';

// --- Helpers ---

function makeTask(overrides: Partial<TaskDetail> = {}): TaskDetail {
  return {
    task_id: 'task-rebuild-1',
    module: 'orchestrator',
    status: 'completed',
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
    child_task_ids: [],
    input_data: { product_id: 'sorafenib', audience: '临床医生' },
    metadata: {},
    ...overrides,
  };
}

function renderTaskDetail(taskId = 'task-rebuild-1') {
  return render(
    <MemoryRouter initialEntries={[`/tasks/${taskId}`]}>
      <Routes>
        <Route path="/tasks/:taskId" element={<TaskDetailPage />} />
        <Route path="/tasks/new" element={<div data-testid="new-task-page">NewTask</div>} />
        <Route path="/tasks/:taskId/rewrite" element={<div data-testid="rewrite-page">Rewrite</div>} />
        <Route path="/tasks/:taskId/review" element={<div data-testid="review-page">Review</div>} />
        <Route path="/tasks/:taskId/compare" element={<div data-testid="compare-page">Compare</div>} />
        <Route path="/" element={<div data-testid="dashboard">Dashboard</div>} />
      </Routes>
    </MemoryRouter>
  );
}

// --- Tests ---

describe('历史任务重建 — _input_source 分流', () => {
  beforeEach(() => {
    localStorage.clear();
    mockGetTaskDetail.mockReset();
  });

  it('metadata._input_source=product → 回填 productId', async () => {
    const user = userEvent.setup();
    mockGetTaskDetail.mockResolvedValue(
      makeTask({
        input_data: { product_id: 'sorafenib', audience: '临床医生' },
        metadata: { _input_source: 'product' },
      }),
    );

    renderTaskDetail();
    const btn = await screen.findByText('使用相同配置新建任务');
    await user.click(btn);

    // 验证导航到新建页
    expect(await screen.findByTestId('new-task-page')).toBeInTheDocument();

    // 验证 localStorage 草稿
    const draft = JSON.parse(localStorage.getItem('xiakedao_new_task_draft')!);
    expect(draft.productId).toBe('sorafenib');
    expect(draft.customTopic).toBe('');
  });

  it('metadata._input_source=custom_topic → 回填 customTopic', async () => {
    const user = userEvent.setup();
    mockGetTaskDetail.mockResolvedValue(
      makeTask({
        input_data: { product_id: '肝细胞癌免疫治疗进展', audience: '临床医生' },
        metadata: { _input_source: 'custom_topic' },
      }),
    );

    renderTaskDetail();
    const btn = await screen.findByText('使用相同配置新建任务');
    await user.click(btn);

    expect(await screen.findByTestId('new-task-page')).toBeInTheDocument();
    const draft = JSON.parse(localStorage.getItem('xiakedao_new_task_draft')!);
    expect(draft.productId).toBe('');
    expect(draft.customTopic).toBe('肝细胞癌免疫治疗进展');
  });

  it('无 _input_source（旧任务） → fallback 到 customTopic', async () => {
    const user = userEvent.setup();
    mockGetTaskDetail.mockResolvedValue(
      makeTask({
        input_data: { product_id: 'legacy-topic', audience: '临床医生' },
        metadata: {},
      }),
    );

    renderTaskDetail();
    const btn = await screen.findByText('使用相同配置新建任务');
    await user.click(btn);

    expect(await screen.findByTestId('new-task-page')).toBeInTheDocument();
    const draft = JSON.parse(localStorage.getItem('xiakedao_new_task_draft')!);
    expect(draft.productId).toBe('');
    expect(draft.customTopic).toBe('legacy-topic');
  });
});

describe('条件项入口 — 改稿/审阅/对比', () => {
  beforeEach(() => {
    localStorage.clear();
    mockGetTaskDetail.mockReset();
    mockGetTaskDetail.mockResolvedValue(makeTask());
  });

  it('任务详情页展示改稿、提交审阅、版本对比入口', async () => {
    renderTaskDetail();
    expect(await screen.findByText('修改文章')).toBeInTheDocument();
    expect(screen.getByText('审阅与批注')).toBeInTheDocument();
    expect(screen.getByText('查看版本对比')).toBeInTheDocument();
  });

  it('点击改稿跳转到 /tasks/:taskId/rewrite', async () => {
    const user = userEvent.setup();
    renderTaskDetail();
    const btn = await screen.findByText('修改文章');
    await user.click(btn);
    expect(await screen.findByTestId('rewrite-page')).toBeInTheDocument();
  });

  it('点击提交审阅跳转到 /tasks/:taskId/review', async () => {
    const user = userEvent.setup();
    renderTaskDetail();
    const btn = await screen.findByText('审阅与批注');
    await user.click(btn);
    expect(await screen.findByTestId('review-page')).toBeInTheDocument();
  });

  it('点击版本对比跳转到 /tasks/:taskId/compare', async () => {
    const user = userEvent.setup();
    renderTaskDetail();
    const btn = await screen.findByText('查看版本对比');
    await user.click(btn);
    expect(await screen.findByTestId('compare-page')).toBeInTheDocument();
  });
});
