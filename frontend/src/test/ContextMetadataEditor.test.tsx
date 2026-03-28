/**
 * ContextMetadataEditor Tests
 * 
 * 覆盖 context_metadata 对象校验的核心场景
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ContextMetadataEditor } from '../components/ContextMetadataEditor';

describe('ContextMetadataEditor', () => {
  describe('空文本', () => {
    it('空文本应为有效状态，不显示错误', () => {
      render(<ContextMetadataEditor value="" onChange={vi.fn()} />);
      
      // 空文本不应显示错误
      expect(screen.queryByText(/无效/)).not.toBeInTheDocument();
      expect(screen.queryByText(/错误/)).not.toBeInTheDocument();
    });
  });

  describe('JSON 对象', () => {
    it('有效的 JSON 对象应被接受', () => {
      const validObject = '{"department": "心内科", "disease_type": "冠心病"}';
      
      render(<ContextMetadataEditor value={validObject} onChange={vi.fn()} />);
      
      // 应显示有效状态
      expect(screen.getByText('JSON 对象有效')).toBeInTheDocument();
    });

    it('嵌套对象应被接受', () => {
      const nestedObject = '{"patient": {"age": 65, "gender": "male"}}';
      
      render(<ContextMetadataEditor value={nestedObject} onChange={vi.fn()} />);
      
      expect(screen.getByText('JSON 对象有效')).toBeInTheDocument();
    });
  });

  describe('JSON 数组', () => {
    it('JSON 数组应被标记为无效', () => {
      const arrayJson = '[1, 2, 3]';
      
      render(<ContextMetadataEditor value={arrayJson} onChange={vi.fn()} />);
      
      // 应显示无效状态
      expect(screen.getByText('无效')).toBeInTheDocument();
      expect(screen.getByText(/类型错误.*数组/)).toBeInTheDocument();
    });
  });

  describe('JSON 字符串/数字/布尔值', () => {
    it('JSON 字符串应被标记为无效', () => {
      const stringJson = '"hello world"';
      
      render(<ContextMetadataEditor value={stringJson} onChange={vi.fn()} />);
      
      expect(screen.getByText('无效')).toBeInTheDocument();
      expect(screen.getByText(/类型错误.*字符串/)).toBeInTheDocument();
    });

    it('JSON 数字应被标记为无效', () => {
      const numberJson = '123';
      
      render(<ContextMetadataEditor value={numberJson} onChange={vi.fn()} />);
      
      expect(screen.getByText('无效')).toBeInTheDocument();
      expect(screen.getByText(/类型错误.*数字/)).toBeInTheDocument();
    });

    it('JSON 布尔值应被标记为无效', () => {
      const boolJson = 'true';
      
      render(<ContextMetadataEditor value={boolJson} onChange={vi.fn()} />);
      
      expect(screen.getByText('无效')).toBeInTheDocument();
      expect(screen.getByText(/类型错误.*布尔值/)).toBeInTheDocument();
    });

    it('JSON null 应被标记为无效', () => {
      const nullJson = 'null';
      
      render(<ContextMetadataEditor value={nullJson} onChange={vi.fn()} />);
      
      expect(screen.getByText('无效')).toBeInTheDocument();
      expect(screen.getByText(/类型错误.*null/)).toBeInTheDocument();
    });
  });

  describe('无效 JSON 语法', () => {
    it('无效 JSON 语法应显示解析错误', () => {
      const invalidJson = '{invalid}';
      
      render(<ContextMetadataEditor value={invalidJson} onChange={vi.fn()} />);
      
      expect(screen.getByText('无效')).toBeInTheDocument();
    });
  });

  describe('用户输入交互', () => {
    it('用户输入应触发 onChange', () => {
      const onChange = vi.fn();
      
      render(<ContextMetadataEditor value="" onChange={onChange} />);
      
      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: '{"key": "value"}' } });
      
      expect(onChange).toHaveBeenCalled();
    });
  });
});