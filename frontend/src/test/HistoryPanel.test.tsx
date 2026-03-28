/**
 * Tests for HistoryPanel
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { HistoryPanel } from '../components/HistoryPanel';

// Mock useTaskHistory hook
vi.mock('../hooks/useTaskHistory', () => ({
  useTaskHistory: vi.fn(() => ({
    tasks: [],
    total: 0,
    loading: false,
    error: null,
    refresh: vi.fn(),
    getDetail: vi.fn(),
    detailCache: new Map(),
    lastRefreshedAt: null,
  })),
}));

describe('HistoryPanel', () => {
  const mockOnLoadParams = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders empty state when no tasks', () => {
    render(<HistoryPanel onLoadParams={mockOnLoadParams} />);
    expect(screen.getByText('暂无历史任务')).toBeInTheDocument();
  });

  it('renders refresh button', () => {
    render(<HistoryPanel onLoadParams={mockOnLoadParams} />);
    expect(screen.getByText('刷新')).toBeInTheDocument();
  });

  it('displays task list when tasks exist', async () => {
    const mockTasks = [
      {
        task_id: 'task-1',
        module: 'opinion',
        status: 'completed',
        started_at: '2026-03-17T00:00:00Z',
      },
    ];

    vi.mocked(await import('../hooks/useTaskHistory')).useTaskHistory.mockReturnValue({
      tasks: mockTasks,
      total: 1,
      loading: false,
      error: null,
      refresh: vi.fn(),
      getDetail: vi.fn().mockResolvedValue({
        task_id: 'task-1',
        module: 'opinion',
        status: 'completed',
        input_data: { audience: '医生' },
        child_task_ids: [],
        started_at: '2026-03-17T00:00:00Z',
      }),
      detailCache: new Map(),
      lastRefreshedAt: new Date(),
    });

    render(<HistoryPanel onLoadParams={mockOnLoadParams} />);
    expect(screen.getByText('观点生成')).toBeInTheDocument();
    expect(screen.getByText('完成')).toBeInTheDocument();
  });

  it('displays error message when error occurs', async () => {
    vi.mocked(await import('../hooks/useTaskHistory')).useTaskHistory.mockReturnValue({
      tasks: [],
      total: 0,
      loading: false,
      error: '加载失败',
      refresh: vi.fn(),
      getDetail: vi.fn(),
      detailCache: new Map(),
      lastRefreshedAt: null,
    });

    render(<HistoryPanel onLoadParams={mockOnLoadParams} />);
    expect(screen.getByText('加载失败')).toBeInTheDocument();
  });
});