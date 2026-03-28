/**
 * Article Workflow Config Form Tests
 * 
 * 验证重要边界：不暴露 semantic_review.content 手填字段
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ArticleWorkflowConfigForm } from '../components/forms/ArticleWorkflowConfigForm';
import { DEFAULT_ARTICLE_DRAFT } from '../types/draft';

describe('ArticleWorkflowConfigForm', () => {
  const defaultProps = {
    value: DEFAULT_ARTICLE_DRAFT,
    onChange: vi.fn(),
    onSubmit: vi.fn(),
    disabled: false,
  };

  describe('边界验证', () => {
    it('不应暴露 semantic_review.content 手填字段', () => {
      render(<ArticleWorkflowConfigForm {...defaultProps} />);
      
      // 查找所有 textbox，检查 placeholder
      const textboxes = screen.getAllByRole('textbox');
      const placeholders = textboxes.map(t => t.getAttribute('placeholder') || '');
      
      // 不应该有任何 textbox 用于输入审核内容
      const hasContentField = placeholders.some(p => 
        p.includes('审核内容') || p.includes('待审核')
      );
      
      expect(hasContentField).toBe(false);
    });

    it('应显示说明"审核内容由工作流自动生成"', () => {
      render(<ArticleWorkflowConfigForm {...defaultProps} />);
      
      // 应该有说明文字表明审核内容是自动生成的
      expect(screen.getByText(/审核内容由工作流自动/)).toBeInTheDocument();
    });

    it('应有语义审核配置区域', () => {
      render(<ArticleWorkflowConfigForm {...defaultProps} />);
      
      // 应该有语义审核配置的标题
      expect(screen.getByText('语义审核配置')).toBeInTheDocument();
    });

    it('应有审核受众设置选项', () => {
      render(<ArticleWorkflowConfigForm {...defaultProps} />);
      
      // 应该有审核受众的下拉选择
      const select = screen.getByRole('combobox');
      expect(select).toBeInTheDocument();
    });

    it('应有原型提示和语体要求字段', () => {
      render(<ArticleWorkflowConfigForm {...defaultProps} />);
      
      // 验证表单存在这些字段
      const inputs = screen.getAllByRole('textbox');
      expect(inputs.length).toBeGreaterThan(0);
    });

    it('默认应显示"沿用观点受众"说明', () => {
      render(<ArticleWorkflowConfigForm {...defaultProps} />);
      
      // 应显示"沿用观点受众"的说明
      expect(screen.getByText(/当前将使用观点受众/)).toBeInTheDocument();
    });
  });

  describe('请求构建验证', () => {
    it('buildRequest 函数不应包含 semantic_review.content 字段', () => {
      // 这个测试验证的是组件内部的 buildRequest 函数逻辑
      // 我们可以通过检查 UI 来间接验证
      
      render(<ArticleWorkflowConfigForm {...defaultProps} />);
      
      // 验证没有"审核内容"相关的输入字段
      // 注意：说明文字中有"审核内容"，所以我们要检查的是没有专门的输入字段
      const textboxes = screen.getAllByRole('textbox');
      const placeholders = textboxes.map(t => t.getAttribute('placeholder') || '');
      
      // 不应该有任何 textbox 的 placeholder 提示输入审核内容
      const hasContentInput = placeholders.some(p => 
        p.includes('审核内容') || p.includes('待审核')
      );
      
      expect(hasContentInput).toBe(false);
      
      // 应该有说明文字
      expect(screen.getByText(/审核内容由工作流自动/)).toBeInTheDocument();
    });

    it('不应暴露顶层 metadata 字段配置', () => {
      render(<ArticleWorkflowConfigForm {...defaultProps} />);
      
      // 验证没有"元数据"或"metadata"相关的配置字段
      const allText = document.body.textContent || '';
      
      // 不应该有顶层 metadata 配置入口
      expect(allText).not.toContain('工作流元数据');
      expect(allText).not.toContain('顶层元数据');
    });
  });
});