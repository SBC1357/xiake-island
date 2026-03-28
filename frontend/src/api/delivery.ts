/**
 * Delivery API Client
 */

import { apiClient, ApiError, API_BASE_URL } from './client';

// ============ Types ============

export interface DeliveryRequest {
  thesis: string;
  outline: Record<string, unknown>[];
  key_evidence?: string[];
  content?: string;
  target_audience?: string;
  play_id?: string;
  arc_id?: string;
}

export interface DeliveryResult {
  task_id: string;
  output_path: string;
  summary: Record<string, unknown>;
  artifacts: string[];
}

export interface DeliveryHistoryItem {
  filename: string;
  path: string;
  created_at?: string;
}

export interface DeliveryHistory {
  items: DeliveryHistoryItem[];
  count: number;
}

// ============ API Functions ============

/**
 * Deliver content
 */
export async function deliverContent(request: DeliveryRequest): Promise<DeliveryResult> {
  return apiClient<DeliveryResult>('/v1/delivery/deliver', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Get delivery history
 */
export async function getDeliveryHistory(): Promise<DeliveryHistory> {
  return apiClient<DeliveryHistory>('/v1/delivery/history');
}

/**
 * Get artifact download URL
 */
export function getArtifactUrl(filename: string): string {
  return `${API_BASE_URL}/v1/delivery/artifact/${filename}`;
}

export { ApiError };