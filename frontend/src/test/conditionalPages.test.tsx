/**
 * 条件项三页（改稿/审阅/对比）集成测试
 *
 * 验证：
 * 1. 加载 → Spinner → 数据渲染
 * 2. API 错误 → 错误信息展示
 * 3. 核心交互（改稿执行、审阅提交、版本接受/回滚）
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

// ====== Mock: tasks ======

const mockGetTaskDetail = vi.fn();

vi.mock('../api/tasks', () => ({
  getTaskDetail: (...args: unknown[]) => mockGetTaskDetail(...args),
}));

// ====== Mock: rewrite ======

const mockExecuteRewrite = vi.fn();
const mockGetRewriteHistory = vi.fn();

vi.mock('../api/rewrite', () => ({
  executeRewrite: (...args: unknown[]) => mockExecuteRewrite(...args),
  getRewriteHistory: (...args: unknown[]) => mockGetRewriteHistory(...args),
}));

// ====== Mock: editorial ======

const mockSubmitEditorialReview = vi.fn();
const mockGetEditorialHistory = vi.fn();

vi.mock('../api/editorial', () => ({
  submitEditorialReview: (...args: unknown[]) => mockSubmitEditorialReview(...args),
  getEditorialHistory: (...args: unknown[]) => mockGetEditorialHistory(...args),
}));

// ====== Mock: versions ======

const mockGetVersionList = vi.fn();
const mockCompareVersions = vi.fn();
const mockAcceptVersion = vi.fn();

vi.mock('../api/versions', () => ({
  getVersionList: (...args: unknown[]) => mockGetVersionList(...args),
  compareVersions: (...args: unknown[]) => mockCompareVersions(...args),
  acceptVersion: (...args: unknown[]) => mockAcceptVersion(...args),
}));

// ====== Mock: client ======

vi.mock('../api/client', () => ({
  ApiError: class ApiError extends Error {
    status: number;
    constructor(message: string, status = 500) {
      super(message);
      this.status = status;
    }
  },
  apiClient: vi.fn(),
}));

// ====== Imports (after mocks) ======

import { RewriteWorkspacePage } from '../pages/RewriteWorkspacePage';
import { EditorialReviewPage } from '../pages/EditorialReviewPage';
import { VersionComparePage } from '../pages/VersionComparePage';

// ====== Helpers ======

function makeTask(overrides = {}) {
  return {
    task_id: 'task-1',
    module: 'orchestrator',
    status: 'completed',
    started_at: new Date().toISOString(),
    child_task_ids: [],
    input_hash: 'hash-abc',
    input_data: { product_id: 'sorafenib' },
    output_data: {
      paragraphs: [
        { id: 'p1', text: '段落一内容', locked: true },
        { id: 'p2', text: '段落二内容' },
      ],
    },
    metadata: {
      brief: {
        locked_sections: ['p1'],
        must_keep_points: ['关键点A'],
        must_delete_points: [],
        forbidden_topics: [],
        word_count_target: { min: 2000, max: 3000 },
        evidence_gaps: [{ position: '§3', missing: '亚组分析' }],
      },
    },
    ...overrides,
  };
}

function renderRewritePage(taskId = 'task-1') {
  return render(
    <MemoryRouter initialEntries={[`/tasks/${taskId}/rewrite`]}>
      <Routes>
        <Route path="/tasks/:taskId/rewrite" element={<RewriteWorkspacePage />} />
        <Route path="/tasks/:taskId" element={<div data-testid="task-detail">Detail</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditorialPage(taskId = 'task-1') {
  return render(
    <MemoryRouter initialEntries={[`/tasks/${taskId}/review`]}>
      <Routes>
        <Route path="/tasks/:taskId/review" element={<EditorialReviewPage />} />
        <Route path="/tasks/:taskId" element={<div data-testid="task-detail">Detail</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderComparePage(taskId = 'task-1') {
  return render(
    <MemoryRouter initialEntries={[`/tasks/${taskId}/compare`]}>
      <Routes>
        <Route path="/tasks/:taskId/compare" element={<VersionComparePage />} />
        <Route path="/tasks/:taskId" element={<div data-testid="task-detail">Detail</div>} />
        <Route path="/tasks/:taskId/rewrite" element={<div data-testid="rewrite-page">Rewrite</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

// ====================================================================
// RewriteWorkspacePage
// ====================================================================

describe('RewriteWorkspacePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetRewriteHistory.mockResolvedValue({ task_id: 'task-1', history: [] });
  });

  it('加载完成后渲染段落', async () => {
    mockGetTaskDetail.mockResolvedValue(makeTask());
    renderRewritePage();

    expect(await screen.findByText('段落一内容')).toBeInTheDocument();
    expect(screen.getByText('段落二内容')).toBeInTheDocument();
  });

  it('API 错误显示错误信息', async () => {
    mockGetTaskDetail.mockRejectedValue(new Error('网络不可达'));
    renderRewritePage();

    expect(await screen.findByText('加载任务详情失败')).toBeInTheDocument();
  });

  it('执行改稿调用 executeRewrite', async () => {
    const user = userEvent.setup();
    mockGetTaskDetail.mockResolvedValue(makeTask());
    mockExecuteRewrite.mockResolvedValue({
      task_id: 'task-1',
      rewrite_task_id: 'rw-1',
      status: 'completed',
      mode: 'expand_patch',
      paragraphs: [
        { paragraph_id: 'p1', old_text: '段落一内容', new_text: '段落一新内容', status: 'modified' },
        { paragraph_id: 'p2', old_text: '段落二内容', new_text: '段落二内容', status: 'unchanged' },
      ],
      word_delta: 3,
    });

    renderRewritePage();

    // 等待段落渲染
    await screen.findByText('段落一内容');

    // 点击执行改稿按钮
    const execBtn = screen.getByRole('button', { name: /投产执行/ });
    await user.click(execBtn);

    await waitFor(() => {
      expect(mockExecuteRewrite).toHaveBeenCalledTimes(1);
    });
  });
});

// ====================================================================
// EditorialReviewPage
// ====================================================================

describe('EditorialReviewPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetEditorialHistory.mockResolvedValue({ task_id: 'task-1', reviews: [] });
  });

  it('加载完成后渲染段落', async () => {
    mockGetTaskDetail.mockResolvedValue(makeTask());
    renderEditorialPage();

    expect(await screen.findByText('段落一内容')).toBeInTheDocument();
    expect(screen.getByText('段落二内容')).toBeInTheDocument();
  });

  it('API 错误显示错误信息', async () => {
    mockGetTaskDetail.mockRejectedValue(new Error('服务器错误'));
    renderEditorialPage();

    expect(await screen.findByText('加载任务详情失败')).toBeInTheDocument();
  });

  it('提交审阅调用 submitEditorialReview', async () => {
    const user = userEvent.setup();
    mockGetTaskDetail.mockResolvedValue(makeTask());
    mockSubmitEditorialReview.mockResolvedValue({
      review_id: 'rev-1',
      task_id: 'task-1',
      decision: 'approved',
      status: 'submitted',
    });

    renderEditorialPage();

    // 等待段落渲染
    await screen.findByText('段落一内容');

    // 必须先选中一个决定才能提交
    const approveBtn = screen.getByText('签发 (Approved)');
    await user.click(approveBtn);

    // 点击提交按钮
    const submitBtn = screen.getByRole('button', { name: /执行最终裁决/ });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(mockSubmitEditorialReview).toHaveBeenCalledTimes(1);
    });
  });
});

// ====================================================================
// VersionComparePage
// ====================================================================

describe('VersionComparePage', () => {
  const mockVersions = [
    { version: 'v1', task_id: 'task-1', label: '初稿', mode: 'initial', created_at: '2026-03-20T10:00:00Z', word_count: 2000, status: 'completed' },
    { version: 'v2', task_id: 'task-1', label: '改稿1', mode: 'expand_patch', created_at: '2026-03-20T12:00:00Z', word_count: 2200, status: 'completed' },
  ];

  const mockCompareResult = {
    left_version: 'v1',
    right_version: 'v2',
    paragraphs: [
      { paragraph_id: 'p1', old_text: '旧段落一', new_text: '新段落一', status: 'modified', locked: false },
      { paragraph_id: 'p2', old_text: '删除的段落', new_text: '', status: 'removed', locked: false },
      { paragraph_id: 'p3', old_text: '', new_text: '新增段落', status: 'added', locked: false },
    ],
    metadata: {
      mode: 'expand_patch',
      word_delta: 200,
      conservation_status: '信息守恒',
      added_points: ['新增论点A'],
      removed_points: [],
    },
    locked_paragraph_warnings: [],
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('加载后渲染版本对比视图', async () => {
    mockGetTaskDetail.mockResolvedValue(makeTask());
    mockGetVersionList.mockResolvedValue({ input_hash: 'hash-abc', versions: mockVersions, total: 2 });
    mockCompareVersions.mockResolvedValue(mockCompareResult);

    renderComparePage();

    // 等待加载完成
    expect(await screen.findByText(/版本对比/)).toBeInTheDocument();

    // 等待对比结果
    await waitFor(() => {
      expect(mockCompareVersions).toHaveBeenCalled();
    });
  });

  it('API 错误显示错误信息', async () => {
    mockGetTaskDetail.mockRejectedValue(new Error('任务不存在'));
    renderComparePage();

    expect(await screen.findByText('加载任务详情失败')).toBeInTheDocument();
  });

  it('无版本时显示空提示', async () => {
    mockGetTaskDetail.mockResolvedValue(makeTask());
    mockGetVersionList.mockResolvedValue({ input_hash: 'hash-abc', versions: [], total: 0 });

    renderComparePage();

    expect(await screen.findByText(/暂无演化版次记录/)).toBeInTheDocument();
  });

  it('接受版本调用 acceptVersion', async () => {
    const user = userEvent.setup();
    mockGetTaskDetail.mockResolvedValue(makeTask());
    mockGetVersionList.mockResolvedValue({ input_hash: 'hash-abc', versions: mockVersions, total: 2 });
    mockCompareVersions.mockResolvedValue(mockCompareResult);
    mockAcceptVersion.mockResolvedValue({
      task_id: 'task-1',
      version: 'v2',
      action: 'accept',
      status: 'completed',
    });

    renderComparePage();

    // 等待对比结果渲染
    await waitFor(() => {
      expect(mockCompareVersions).toHaveBeenCalled();
    });

    // 点击接受按钮
    const acceptBtn = await screen.findByRole('button', { name: /并入主轨/ });
    await user.click(acceptBtn);

    await waitFor(() => {
      expect(mockAcceptVersion).toHaveBeenCalledWith({
        task_id: 'task-1',
        version: 'v2',
        action: 'accept',
      });
    });
  });

  it('锁定段落被修改时显示警告', async () => {
    mockGetTaskDetail.mockResolvedValue(makeTask());
    mockGetVersionList.mockResolvedValue({ input_hash: 'hash-abc', versions: mockVersions, total: 2 });
    mockCompareVersions.mockResolvedValue({
      ...mockCompareResult,
      paragraphs: [
        { paragraph_id: 'p1', old_text: '旧文本', new_text: '新文本', status: 'modified', locked: true },
      ],
    });

    renderComparePage();

    // 页面中有多处 "锁定段落被修改"（⚠ 提示 + Badge），取全部并验证存在
    const warnings = await screen.findAllByText(/文章修改约束警告|已锁定设定|越权违规/);
    expect(warnings.length).toBeGreaterThan(0);
  });
});
