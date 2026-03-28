/**
 * Evidence Upload API Client
 *
 * 多模态证据文件上传与回溯查询 API。
 */

import { API_BASE_URL, ApiError } from './client';

// ============ Types ============

export interface TracebackInfo {
  original_file: Record<string, unknown>;
  page_image: Record<string, unknown>;
  fragment: Record<string, unknown>;
}

export interface TraceableEvidence {
  evidence_id: string;
  upload_id: string;
  content: string;
  source_file: string;
  source_pages: number[];
  evidence_type: string;
  status: string;
  confidence?: number;
  traceback: Record<string, unknown>;
}

export interface PageImageInfo {
  image_id: string;
  page_number: number;
  width: number;
  height: number;
  format: string;
}

export interface EvidenceFragmentInfo {
  fragment_id: string;
  page_number: number;
  fragment_type: string;
  content: string;
  confidence: number;
  source_location?: string;
}

export interface UploadResponse {
  upload_id: string;
  original_filename: string;
  file_type: string;
  status: string;
  error_message?: string;
  page_count: number;
  fragment_count: number;
  evidence_count: number;
  evidences: TraceableEvidence[];
}

export interface UploadStatusResponse {
  upload_id: string;
  original_filename: string;
  file_type: string;
  file_size_bytes: number;
  status: string;
  task_id?: string;
  error_message?: string;
  page_images: PageImageInfo[];
  fragments: EvidenceFragmentInfo[];
  evidences: TraceableEvidence[];
}

export interface UploadListResponse {
  uploads: UploadResponse[];
  total: number;
}

// ============ API Functions ============

const ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.jpg', '.jpeg', '.png'];

/**
 * 上传多模态证据文件
 */
export async function uploadEvidenceFile(
  file: File,
  taskId?: string
): Promise<UploadResponse> {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    throw new ApiError(400, `不支持的文件格式: ${ext}`);
  }

  const formData = new FormData();
  formData.append('file', file);
  if (taskId) formData.append('task_id', taskId);

  const response = await fetch(`${API_BASE_URL}/v1/evidence/upload/file`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new ApiError(response.status, data.detail || 'Upload failed');
  }

  return response.json();
}

/**
 * 获取上传状态与详情
 */
export async function getUploadStatus(uploadId: string): Promise<UploadStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/evidence/upload/status/${uploadId}`);
  if (!response.ok) throw new ApiError(response.status, 'Failed to get upload status');
  return response.json();
}

/**
 * 获取上传文件的可回溯证据
 */
export async function getUploadEvidences(uploadId: string): Promise<TraceableEvidence[]> {
  const response = await fetch(`${API_BASE_URL}/v1/evidence/upload/evidences/${uploadId}`);
  if (!response.ok) throw new ApiError(response.status, 'Failed to get evidences');
  return response.json();
}

/**
 * 获取指定任务关联的所有可回溯证据
 */
export async function getTaskEvidences(taskId: string): Promise<TraceableEvidence[]> {
  const response = await fetch(`${API_BASE_URL}/v1/evidence/upload/task/${taskId}/evidences`);
  if (!response.ok) throw new ApiError(response.status, 'Failed to get task evidences');
  return response.json();
}

/**
 * 列出上传记录
 */
export async function listUploads(taskId?: string): Promise<UploadListResponse> {
  const params = taskId ? `?task_id=${taskId}` : '';
  const response = await fetch(`${API_BASE_URL}/v1/evidence/upload/list${params}`);
  if (!response.ok) throw new ApiError(response.status, 'Failed to list uploads');
  return response.json();
}

export { ApiError };
