/**
 * Versions API — 版本对比页联调契约
 *
 * 端点映射:
 *   - 版本列表:       GET  /v1/tasks/versions/{input_hash} (复用)
 *   - 版本对比:       GET  /v1/versions/compare
 *   - 接受/回滚版本:  POST /v1/versions/accept
 */

import { apiClient } from './client';

// ==================== 类型定义 ====================

export interface VersionMeta {
  version: string;
  task_id: string;
  label: string;
  mode: string;
  created_at: string;
  word_count: number;
  status: string;
}

export interface VersionListResponse {
  input_hash: string;
  versions: VersionMeta[];
  total: number;
}

export interface ParagraphDiff {
  paragraph_id: string;
  old_text: string;
  new_text: string;
  status: 'unchanged' | 'added' | 'removed' | 'modified';
  locked: boolean;
}

export interface CompareMetadata {
  mode: string;
  word_delta: number;
  conservation_status: string;
  added_points: string[];
  removed_points: string[];
}

export interface VersionCompareResponse {
  left_version: string;
  right_version: string;
  paragraphs: ParagraphDiff[];
  metadata: CompareMetadata;
  locked_paragraph_warnings: string[];
}

export interface VersionAcceptRequest {
  task_id: string;
  version: string;
  action: 'accept' | 'rollback';
}

export interface VersionAcceptResponse {
  task_id: string;
  version: string;
  action: 'accept' | 'rollback';
  status: 'completed' | 'failed';
  error?: string;
}

// ==================== API 函数 ====================

/**
 * 获取版本列表
 */
export async function getVersionList(inputHash: string): Promise<VersionListResponse> {
  return apiClient<VersionListResponse>(`/v1/tasks/versions/${encodeURIComponent(inputHash)}`);
}

/**
 * 获取两个版本的对比结果
 */
export async function compareVersions(
  taskId: string,
  leftVersion: string,
  rightVersion: string,
): Promise<VersionCompareResponse> {
  const params = new URLSearchParams({
    task_id: taskId,
    left: leftVersion,
    right: rightVersion,
  });
  return apiClient<VersionCompareResponse>(`/v1/versions/compare?${params}`);
}

/**
 * 接受或回滚到指定版本
 */
export async function acceptVersion(request: VersionAcceptRequest): Promise<VersionAcceptResponse> {
  return apiClient<VersionAcceptResponse>('/v1/versions/accept', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}
