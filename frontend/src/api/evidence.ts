/**
 * Evidence API Client
 */

import { apiClient, ApiError } from './client';

// ============ Types ============

export interface EvidenceQueryRequest {
  product_id: string;
  domain?: string;
  fact_keys?: string[];
  limit?: number;
}

export interface FactRecord {
  fact_id: string;
  product_id: string;
  domain: string;
  fact_key: string;
  value: string;
  definition?: string;
  definition_zh?: string;
  unit?: string;
  status: string;
  lineage: Record<string, unknown>;
}

export interface SourceRecord {
  source_id: string;
  source_type: string;
  title: string;
  product_id?: string;
  source_keys: string[];
}

export interface FactLineage {
  fact_id: string;
  product_id?: string;
  lineage: Record<string, unknown>;
  sources: string[];
}

export interface ProductListResponse {
  products: string[];
  count: number;
}

// ============ API Functions ============

/**
 * Query evidence facts
 */
export async function queryEvidence(request: EvidenceQueryRequest): Promise<FactRecord[]> {
  return apiClient<FactRecord[]>('/v1/evidence/query', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Get fact detail with lineage
 */
export async function getFactDetail(factId: string): Promise<FactLineage> {
  return apiClient<FactLineage>(`/v1/evidence/fact/${factId}`);
}

/**
 * List available products
 */
export async function listProducts(): Promise<ProductListResponse> {
  return apiClient<ProductListResponse>('/v1/evidence/products');
}

/**
 * Get sources for a product
 */
export async function getSources(productId: string, sourceType?: string): Promise<SourceRecord[]> {
  const params = sourceType ? `?source_type=${sourceType}` : '';
  return apiClient<SourceRecord[]>(`/v1/evidence/sources/${productId}${params}`);
}

// ============ Evidence Stats ============

export interface EvidenceStatsResponse {
  total_facts: number;
  total_sources: number;
  total_products: number;
  source_type_distribution: Record<string, number>;
  products: string[];
  freshness: string | null;
}

/**
 * Get evidence statistics summary
 */
export async function getEvidenceStats(): Promise<EvidenceStatsResponse> {
  return apiClient<EvidenceStatsResponse>('/v1/evidence/stats');
}

export { ApiError };