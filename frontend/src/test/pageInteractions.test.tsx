/**
 * 关键交互验证 — NewTaskPage 工作流选择 + 任务重建回填
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

vi.mock('../api/evidence', () => ({
  listProducts: vi.fn().mockResolvedValue({ products: ['TestProduct'] }),
}));

vi.mock('../api/workflow', () => ({
  executeStandardChainWorkflow: vi.fn().mockResolvedValue({ task_id: 'new-1', child_task_ids: [], status: 'running', result: null, child_results: [], errors: [] }),
  executeArticleWorkflow: vi.fn(),
}));

import { NewTaskPage } from '../pages/NewTaskPage';

function renderNewTask() {
  return render(
    <MemoryRouter initialEntries={['/tasks/new']}>
      <Routes>
        <Route path="/tasks/new" element={<NewTaskPage />} />
        <Route path="/workflow/article" element={<div data-testid="article-page">Article Page</div>} />
        <Route path="/tasks/:taskId" element={<div data-testid="task-detail">Task Detail</div>} />
      </Routes>
    </MemoryRouter>
  );
}

describe('NewTaskPage 工作流选择', () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  it('默认选中标准图谱六段链', async () => {
    renderNewTask();
    const stdCard = await screen.findByText('标准图谱六段链');
    expect(stdCard.closest('button')).toHaveClass('border-brand-500');
  });

  it('选择文章工作流后分步按钮显示仅限六段链可用', async () => {
    const user = userEvent.setup();
    renderNewTask();
    const articleBtn = await screen.findByText('通用文章直出工作流');
    await user.click(articleBtn);
    expect(screen.getByText('仅限六段链可用')).toBeInTheDocument();
  });

  it('选择文章工作流后分步模式不可用', async () => {
    const user = userEvent.setup();
    renderNewTask();
    const articleBtn = await screen.findByText('通用文章直出工作流');
    await user.click(articleBtn);
    expect(screen.getByText('仅限六段链可用')).toBeInTheDocument();
  });
});

describe('历史任务重建回填', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('草稿数据能从 localStorage 恢复', async () => {
    const draft = {
      taskName: '回填测试',
      productId: 'TestProduct',
      customTopic: '',
      workflow: 'standard_chain',
      audience: '临床医生',
      projectName: 'P1',
      targetWordCount: 3000,
      register: 'clinical',
      notes: '',
    };
    localStorage.setItem('xiakedao_new_task_draft', JSON.stringify(draft));

    renderNewTask();
    // 草稿恢复后应显示提示
    expect(await screen.findByText('检测到未完成的草稿')).toBeInTheDocument();
  });
});
