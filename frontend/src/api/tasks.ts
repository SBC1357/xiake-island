/**
 * Tasks API
 * 
 * 任务历史查询 API 客户端
 */

import { apiClient, ApiError } from './client';

// ==================== 类型定义 ====================

export interface TaskListItem {
  task_id: string;
  module: string;
  status: string;
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
  error_message?: string;
  input_hash?: string;
}

export interface TaskListResponse {
  tasks: TaskListItem[];
  total: number;
}

export interface TaskDetail {
  task_id: string;
  module: string;
  status: string;
  input_hash?: string;
  input_data?: Record<string, unknown>;
  output_data?: Record<string, unknown>;
  parent_task_id?: string;
  child_task_ids: string[];
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
  metadata?: Record<string, unknown>;
  error_message?: string;
}

export interface TasksQueryParams {
  module?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

// ==================== API 函数 ====================

/**
 * 获取任务列表
 */
export async function listTasks(params: TasksQueryParams = {}): Promise<TaskListResponse> {
  const searchParams = new URLSearchParams();
  
  if (params.module) searchParams.append('module', params.module);
  if (params.status) searchParams.append('status', params.status);
  if (params.limit) searchParams.append('limit', String(params.limit));
  if (params.offset) searchParams.append('offset', String(params.offset));
  
  const queryString = searchParams.toString();
  const endpoint = queryString ? `/v1/tasks?${queryString}` : '/v1/tasks';
  
  return apiClient<TaskListResponse>(endpoint);
}

/**
 * 获取任务详情
 */
export async function getTaskDetail(taskId: string): Promise<TaskDetail> {
  return apiClient<TaskDetail>(`/v1/tasks/${taskId}`);
}

/**
 * 复制任务输入参数创建新任务记录
 * 
 * 注意：此接口仅创建新任务记录，不会实际执行任务。
 */
export async function copyTask(taskId: string): Promise<{ new_task_id: string; original_task_id: string; message: string }> {
  return apiClient<{ new_task_id: string; original_task_id: string; message: string }>(`/v1/tasks/${taskId}/copy`, {
    method: 'POST',
  });
}

/**
 * 获取任务版本列表
 */
export async function getTaskVersions(inputHash: string, limit: number = 20): Promise<{ input_hash: string; versions: TaskListItem[]; total: number }> {
  return apiClient<{ input_hash: string; versions: TaskListItem[]; total: number }>(`/v1/tasks/versions/${inputHash}?limit=${limit}`);
}

export { ApiError };