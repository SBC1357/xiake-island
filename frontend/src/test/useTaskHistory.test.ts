/**
 * Tests for useTaskHistory hook
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useTaskHistory } from '../hooks/useTaskHistory';
import * as tasksApi from '../api/tasks';

// Mock tasks API
vi.mock('../api/tasks', () => ({
  listTasks: vi.fn(),
  getTaskDetail: vi.fn(),
}));

describe('useTaskHistory', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns initial empty state', () => {
    vi.mocked(tasksApi.listTasks).mockResolvedValue({ tasks: [], total: 0 });

    const { result } = renderHook(() => useTaskHistory({ autoLoad: false }));

    expect(result.current.tasks).toEqual([]);
    expect(result.current.total).toBe(0);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('does not load when autoLoad is false', () => {
    vi.mocked(tasksApi.listTasks).mockResolvedValue({ tasks: [], total: 0 });

    renderHook(() => useTaskHistory({ autoLoad: false }));

    expect(tasksApi.listTasks).not.toHaveBeenCalled();
  });

  it('getDetail returns task detail', async () => {
    const mockDetail = {
      task_id: 'task-1',
      module: 'opinion',
      status: 'completed',
      input_data: { audience: '医生' },
      child_task_ids: [],
      started_at: '2026-03-17T00:00:00Z',
    };

    vi.mocked(tasksApi.listTasks).mockResolvedValue({ tasks: [], total: 0 });
    vi.mocked(tasksApi.getTaskDetail).mockResolvedValue(mockDetail);

    const { result } = renderHook(() => useTaskHistory({ autoLoad: false }));

    const detail = await result.current.getDetail('task-1');

    expect(detail).toEqual(mockDetail);
    expect(tasksApi.getTaskDetail).toHaveBeenCalledWith('task-1');
  });

  it('getDetail caches results', async () => {
    const mockDetail = {
      task_id: 'task-1',
      module: 'opinion',
      status: 'completed',
      input_data: { audience: '医生' },
      child_task_ids: [],
      started_at: '2026-03-17T00:00:00Z',
    };

    vi.mocked(tasksApi.listTasks).mockResolvedValue({ tasks: [], total: 0 });
    vi.mocked(tasksApi.getTaskDetail).mockResolvedValue(mockDetail);

    const { result } = renderHook(() => useTaskHistory({ autoLoad: false }));

    // First call
    await result.current.getDetail('task-1');
    // Second call - should use cache
    await result.current.getDetail('task-1');

    // API should only be called once due to caching
    expect(tasksApi.getTaskDetail).toHaveBeenCalledTimes(1);
  });

  it('refresh function is available', () => {
    vi.mocked(tasksApi.listTasks).mockResolvedValue({ tasks: [], total: 0 });

    const { result } = renderHook(() => useTaskHistory({ autoLoad: false }));

    expect(typeof result.current.refresh).toBe('function');
  });
});