import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { StandardChainConfigForm } from '../components/forms/StandardChainConfigForm';

const { compileDraftMock, reviewQualityMock } = vi.hoisted(() => ({
  compileDraftMock: vi.fn(),
  reviewQualityMock: vi.fn(),
}));

vi.mock('../api', () => {
  class MockApiError extends Error {}

  return {
    compileDraft: compileDraftMock,
    reviewQuality: reviewQualityMock,
    ApiError: MockApiError,
  };
});

vi.mock('../components/EvidenceQueryPanel', () => ({
  EvidenceQueryPanel: ({ onFactsSelected }: { onFactsSelected?: (facts: Array<Record<string, unknown>>) => void }) => (
    <button
      type="button"
      onClick={() =>
        onFactsSelected?.([
          {
            fact_id: 'fact-1',
            product_id: 'lecanemab',
            domain: 'efficacy',
            fact_key: 'p_value',
            value: '<0.001',
            status: 'approved',
            lineage: {},
          },
        ])
      }
    >
      mock-select-facts
    </button>
  ),
}));

vi.mock('../components/PlanningConfigForm', () => ({
  PlanningConfigForm: ({ onPlanGenerated }: { onPlanGenerated?: (plan: Record<string, unknown>) => void }) => (
    <button
      type="button"
      onClick={() =>
        onPlanGenerated?.({
          task_id: 'plan-1',
          thesis: '测试论点',
          outline: [{ title: '第一部分', type: 'section', domain: 'efficacy' }],
          play_id: 'standard',
          arc_id: 'news',
          target_audience: '医学专业人士',
          key_evidence: ['fact-1'],
        })
      }
    >
      mock-generate-plan
    </button>
  ),
}));

vi.mock('../components/DraftingPanel', () => ({
  DraftingPanel: ({ onDraftingComplete }: { onDraftingComplete?: (result: Record<string, unknown>) => void }) => (
    <button
      type="button"
      onClick={() =>
        onDraftingComplete?.({
          task_id: 'draft-1',
          content: '这是成稿正文',
          word_count: 6,
          trace: { generation_mode: 'fake' },
          metadata: {},
        })
      }
    >
      mock-complete-drafting
    </button>
  ),
}));

vi.mock('../components/DeliveryPanel', () => ({
  DeliveryPanel: ({ content }: { content?: string }) => <div>delivery-content:{content ?? 'missing'}</div>,
}));

describe('StandardChainConfigForm', () => {
  beforeEach(() => {
    compileDraftMock.mockReset();
    reviewQualityMock.mockReset();
  });

  it('keeps writing, drafting, quality, and delivery boundaries aligned to drafting content', async () => {
    const user = userEvent.setup();

    compileDraftMock.mockResolvedValue({
      task_id: 'write-1',
      system_prompt: 'System prompt',
      user_prompt: 'User prompt',
      llm_config: {},
      extra_info: {},
    });
    reviewQualityMock.mockResolvedValue({
      task_id: 'quality-1',
      overall_status: 'passed',
      gates_passed: ['basic'],
      warnings: [],
      errors: [],
    });

    render(<StandardChainConfigForm />);

    await user.click(screen.getByRole('button', { name: 'mock-select-facts' }));
    await user.click(screen.getByRole('button', { name: 'mock-generate-plan' }));

    expect(screen.getByRole('button', { name: '生成写作指令' })).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: '生成写作指令' }));

    await waitFor(() => {
      expect(compileDraftMock).toHaveBeenCalledWith({
        thesis: '测试论点',
        outline: [{ title: '第一部分', type: 'section', domain: 'efficacy' }],
        play_id: 'standard',
        arc_id: 'news',
        target_audience: '医学专业人士',
        key_evidence: ['fact-1'],
      });
    });

    await user.click(screen.getByRole('button', { name: 'mock-complete-drafting' }));

    await waitFor(() => {
      expect(reviewQualityMock).toHaveBeenCalledWith({ content: '这是成稿正文' });
    });

    expect(screen.getByText('审核内容预览')).toBeInTheDocument();
    expect(screen.getByText('这是成稿正文')).toBeInTheDocument();
    expect(screen.queryByText('User prompt')).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: '继续交付' }));

    expect(screen.getByText('delivery-content:这是成稿正文')).toBeInTheDocument();
  });
});
