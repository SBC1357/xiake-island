/**
 * SP-3 E2E Acceptance Test
 *
 * SP-7D: 更新为六段链测试 - Evidence → Planning → Writing → Drafting → Quality → Delivery
 *
 * Demonstrates that the frontend API clients can trigger the backend workflow APIs.
 * This test verifies the integration between frontend components and backend APIs.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { queryEvidence, listProducts } from '../api/evidence';
import { generatePlan } from '../api/planning';
import { compileDraft } from '../api/writing';
import { executeDrafting } from '../api/drafting';
import { reviewQuality } from '../api/quality';
import { deliverContent, getDeliveryHistory } from '../api/delivery';

// Mock fetch globally
const mockFetch = vi.fn();
(globalThis as unknown as { fetch: typeof mockFetch }).fetch = mockFetch;

describe('SP-3 Frontend-Backend Integration', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Evidence API Client', () => {
    it('should call POST /v1/evidence/query with correct payload', async () => {
      const mockResponse = [
        {
          fact_id: 'f1',
          product_id: 'lecanemab',
          domain: 'efficacy',
          fact_key: 'p_value',
          value: '<0.001',
          status: 'approved',
          lineage: {},
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await queryEvidence({
        product_id: 'lecanemab',
        domain: 'efficacy',
        limit: 50,
      });

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/v1/evidence/query');
      expect(options.method).toBe('POST');
      expect(JSON.parse(options.body)).toEqual({
        product_id: 'lecanemab',
        domain: 'efficacy',
        limit: 50,
      });
      expect(result).toEqual(mockResponse);
    });

    it('should call GET /v1/evidence/products to list available products', async () => {
      const mockResponse = { products: ['lecanemab', 'aducanumab'], count: 2 };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await listProducts();

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url] = mockFetch.mock.calls[0];
      expect(url).toContain('/v1/evidence/products');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Planning API Client', () => {
    it('should call POST /v1/planning/plan with correct payload', async () => {
      const mockResponse = {
        task_id: 'task-123',
        thesis: 'Lecanemab shows significant efficacy',
        outline: [
          { title: 'Introduction', type: 'section' },
          { title: 'Efficacy Data', type: 'section' },
        ],
        play_id: 'standard',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await generatePlan({
        context: {
          product_id: 'lecanemab',
          audience: '医学专业人士',
        },
        evidence_facts: [{ fact_id: 'f1', value: 'test' }],
      });

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/v1/planning/plan');
      expect(options.method).toBe('POST');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Writing API Client', () => {
    it('should call POST /v1/writing/draft with correct payload', async () => {
      const mockResponse = {
        task_id: 'task-456',
        system_prompt: 'You are a medical writer...',
        user_prompt: 'Write about lecanemab...',
        llm_config: {},
        extra_info: {},
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await compileDraft({
        thesis: 'Lecanemab is effective',
        outline: [{ title: 'Intro', type: 'section' }],
        target_audience: '医学专业人士',
      });

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/v1/writing/draft');
      expect(options.method).toBe('POST');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Drafting API Client', () => {
    it('should call POST /v1/drafting/generate with correct payload', async () => {
      const mockResponse = {
        task_id: 'task-drafting',
        content: 'Generated article content',
        word_count: 120,
        trace: { generation_mode: 'fake' },
        metadata: {},
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await executeDrafting({
        system_prompt: 'You are a medical writer...',
        user_prompt: 'Write about lecanemab...',
        target_word_count: 120,
        metadata: { product_id: 'lecanemab' },
      });

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/v1/drafting/generate');
      expect(options.method).toBe('POST');
      expect(JSON.parse(options.body)).toEqual({
        system_prompt: 'You are a medical writer...',
        user_prompt: 'Write about lecanemab...',
        target_word_count: 120,
        metadata: { product_id: 'lecanemab' },
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Quality API Client', () => {
    it('should call POST /v1/quality/review with correct payload', async () => {
      const mockResponse = {
        task_id: 'task-789',
        overall_status: 'passed',
        gates_passed: ['basic', 'length'],
        warnings: [],
        errors: [],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await reviewQuality({
        content: 'This is a test content for quality review.',
      });

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/v1/quality/review');
      expect(options.method).toBe('POST');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Delivery API Client', () => {
    it('should call POST /v1/delivery/deliver with correct payload', async () => {
      const mockResponse = {
        task_id: 'task-delivery',
        output_path: '/output/article.md',
        summary: {},
        artifacts: ['/output/article.md'],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await deliverContent({
        thesis: 'Lecanemab is effective',
        outline: [{ title: 'Intro', type: 'section' }],
      });

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/v1/delivery/deliver');
      expect(options.method).toBe('POST');
      expect(result).toEqual(mockResponse);
    });

    it('should call GET /v1/delivery/history to list deliveries', async () => {
      const mockResponse = {
        items: [
          { filename: 'article-1.md', path: '/output/article-1.md' },
        ],
        count: 1,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await getDeliveryHistory();

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url] = mockFetch.mock.calls[0];
      expect(url).toContain('/v1/delivery/history');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Standard Chain Flow Simulation', () => {
    it('should demonstrate the complete standard chain API call sequence', async () => {
      // Step 1: Query Evidence
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [{ fact_id: 'f1', product_id: 'lecanemab', domain: 'efficacy', fact_key: 'p_value', value: '<0.001', status: 'approved', lineage: {} }],
      });

      const evidenceResult = await queryEvidence({ product_id: 'lecanemab', limit: 10 });
      expect(evidenceResult).toHaveLength(1);

      // Step 2: Generate Plan
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ task_id: 'plan-1', thesis: 'Test thesis', outline: [] }),
      });

      const planResult = await generatePlan({
        context: { product_id: 'lecanemab', audience: '医学专业人士' },
        evidence_facts: evidenceResult as unknown as Record<string, unknown>[],
      });
      expect(planResult.task_id).toBe('plan-1');

      // Ensure thesis exists for subsequent calls
      const thesis = planResult.thesis ?? 'Default thesis';

      // Step 3: Compile Draft (Writing)
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ task_id: 'write-1', system_prompt: 'System', user_prompt: 'User', llm_config: {}, extra_info: {} }),
      });

      const writeResult = await compileDraft({
        thesis: thesis,
        outline: planResult.outline as unknown as Record<string, unknown>[],
      });
      expect(writeResult.task_id).toBe('write-1');

      // Step 4: Drafting (成稿) - SP-7D: New step between Writing and Quality
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          task_id: 'draft-1',
          content: 'Generated article content...',
          word_count: 500,
          trace: { generation_mode: 'fake' },
          metadata: {}
        }),
      });

      const draftingResult = await executeDrafting({
        system_prompt: writeResult.system_prompt,
        user_prompt: writeResult.user_prompt,
      });
      expect(draftingResult.task_id).toBe('draft-1');
      expect(draftingResult.content).toBeDefined();

      // Step 5: Quality Review - 审核成稿内容
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ task_id: 'quality-1', overall_status: 'passed', gates_passed: ['basic'], warnings: [], errors: [] }),
      });

      const qualityResult = await reviewQuality({ content: draftingResult.content });
      expect(qualityResult.overall_status).toBe('passed');

      // Step 6: Deliver
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ task_id: 'delivery-1', output_path: '/output/test.md', summary: {}, artifacts: [] }),
      });

      const deliveryResult = await deliverContent({
        thesis: thesis,
        outline: planResult.outline as unknown as Record<string, unknown>[],
        content: draftingResult.content,
      });
      expect(deliveryResult.task_id).toBe('delivery-1');

      // Verify the complete chain made 6 API calls (SP-7D: 6 steps)
      expect(mockFetch).toHaveBeenCalledTimes(6);

      // Verify the sequence of endpoints
      const calledEndpoints = mockFetch.mock.calls.map(([url]) => {
        const match = url.match(/\/v1\/[\w/]+/);
        return match ? match[0] : url;
      });

      expect(calledEndpoints[0]).toContain('/v1/evidence/query');
      expect(calledEndpoints[1]).toContain('/v1/planning/plan');
      expect(calledEndpoints[2]).toContain('/v1/writing/draft');
      expect(calledEndpoints[3]).toContain('/v1/drafting/generate');
      expect(calledEndpoints[4]).toContain('/v1/quality/review');
      expect(calledEndpoints[5]).toContain('/v1/delivery/deliver');
    });
  });
});
