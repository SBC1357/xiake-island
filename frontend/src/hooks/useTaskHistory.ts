/**
 * useTaskHistory Hook
 *
 * 任务历史查询 Hook，支持缓存和自动刷新
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { listTasks, getTaskDetail, type TaskListItem, type TaskDetail, type TasksQueryParams } from '../api/tasks';

export interface UseTaskHistoryOptions {
  /** 自动刷新间隔（毫秒），0 表示不自动刷新 */
  refreshInterval?: number;
  /** 默认查询参数 */
  defaultParams?: TasksQueryParams;
  /** 是否在挂载时自动加载 */
  autoLoad?: boolean;
}

export interface UseTaskHistoryReturn {
  /** 任务列表 */
  tasks: TaskListItem[];
  /** 总数量 */
  total: number;
  /** 是否正在加载 */
  loading: boolean;
  /** 错误信息 */
  error: string | null;
  /** 刷新任务列表 */
  refresh: () => Promise<void>;
  /** 获取任务详情 */
  getDetail: (taskId: string) => Promise<TaskDetail | null>;
  /** 任务详情缓存 */
  detailCache: Map<string, TaskDetail>;
  /** 上次刷新时间 */
  lastRefreshedAt: Date | null;
}

// 全局缓存，避免跨组件重复请求
const globalTaskCache = {
  tasks: [] as TaskListItem[],
  total: 0,
  lastFetchedAt: null as Date | null,
  CACHE_TTL: 5000, // 5 秒缓存
};

export function useTaskHistory(options: UseTaskHistoryOptions = {}): UseTaskHistoryReturn {
  const {
    refreshInterval = 0,
    defaultParams = {},
    autoLoad = true,
  } = options;

  const [tasks, setTasks] = useState<TaskListItem[]>(globalTaskCache.tasks);
  const [total, setTotal] = useState(globalTaskCache.total);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<Date | null>(globalTaskCache.lastFetchedAt);

  // 详情缓存
  const detailCacheRef = useRef(new Map<string, TaskDetail>());

  // 是否已挂载
  const mountedRef = useRef(true);

  // 刷新任务列表
  const refresh = useCallback(async () => {
    // 检查缓存是否有效
    const now = new Date();
    if (
      globalTaskCache.lastFetchedAt &&
      now.getTime() - globalTaskCache.lastFetchedAt.getTime() < globalTaskCache.CACHE_TTL
    ) {
      setTasks(globalTaskCache.tasks);
      setTotal(globalTaskCache.total);
      setLastRefreshedAt(globalTaskCache.lastFetchedAt);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await listTasks(defaultParams);

      if (mountedRef.current) {
        setTasks(response.tasks);
        setTotal(response.total);
        setLastRefreshedAt(now);

        // 更新全局缓存
        globalTaskCache.tasks = response.tasks;
        globalTaskCache.total = response.total;
        globalTaskCache.lastFetchedAt = now;
      }
    } catch (e) {
      if (mountedRef.current) {
        const message = e instanceof Error ? e.message : '加载失败';
        setError(message);
      }
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [defaultParams]);

  // 获取任务详情
  const getDetail = useCallback(async (taskId: string): Promise<TaskDetail | null> => {
    // 检查缓存
    const cached = detailCacheRef.current.get(taskId);
    if (cached) {
      return cached;
    }

    try {
      const detail = await getTaskDetail(taskId);
      detailCacheRef.current.set(taskId, detail);
      return detail;
    } catch (e) {
      console.error('Failed to get task detail:', e);
      return null;
    }
  }, []);

  // 挂载时加载
  useEffect(() => {
    mountedRef.current = true;

    if (autoLoad) {
      refresh();
    }

    return () => {
      mountedRef.current = false;
    };
  }, [autoLoad, refresh]);

  // 自动刷新
  useEffect(() => {
    if (refreshInterval <= 0) return;

    const intervalId = setInterval(() => {
      refresh();
    }, refreshInterval);

    return () => {
      clearInterval(intervalId);
    };
  }, [refreshInterval, refresh]);

  return {
    tasks,
    total,
    loading,
    error,
    refresh,
    getDetail,
    detailCache: detailCacheRef.current,
    lastRefreshedAt,
  };
}