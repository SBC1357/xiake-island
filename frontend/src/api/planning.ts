/**
 * Planning API Client
 */

import { apiClient, ApiError } from './client';

// ============ Types ============

export interface RouteContextRequest {
  product_id: string;
  register?: string;
  audience: string;
  project_name?: string;
  deliverable_type?: string;
  metadata?: Record<string, unknown>;
}

export interface PlanningRequest {
  context: RouteContextRequest;
  evidence_facts?: Record<string, unknown>[];
  selected_facts?: string[];
}

export interface OutlineItem {
  title: string;
  type: string;
  domain?: string;
  fact_count?: number;
  fact_id?: string;
}

export interface PlanningResponse {
  task_id: string;
  thesis?: string;
  outline: OutlineItem[];
  play_id?: string;
  arc_id?: string;
  target_audience?: string;
  key_evidence?: string[];
  style_notes?: Record<string, unknown>;
}

export interface PersonaProfile {
  profile_id: string;
  author_id?: string;
  author_name?: string;
  domain?: string;
  tone?: string;
  voice_styles?: string[];
  signature_phrases?: string[];
}

// ============ API Functions ============

/**
 * Generate editorial plan
 */
export async function generatePlan(request: PlanningRequest): Promise<PlanningResponse> {
  return apiClient<PlanningResponse>('/v1/planning/plan', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Get persona profile
 */
export async function getPersona(profileId: string): Promise<PersonaProfile | null> {
  return apiClient<PersonaProfile | null>('/v1/planning/persona', {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId }),
  });
}

export { ApiError };