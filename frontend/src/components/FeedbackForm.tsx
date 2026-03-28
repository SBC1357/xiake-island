/**
 * FeedbackForm
 *
 * 任务反馈表单组件
 */

import { useState, useCallback } from 'react';
import { Button } from './ui/Button';
import { useFeedback } from '../hooks/useFeedback';

export interface FeedbackFormProps {
  /** 任务ID */
  taskId: string;
  /** 提交成功后的回调 */
  onSuccess?: () => void;
}

const RATING_LABELS = ['很差', '较差', '一般', '较好', '很好'];
const PRESET_TAGS = ['内容准确', '逻辑清晰', '格式规范', '需补充', '有错误'];

export function FeedbackForm({ taskId, onSuccess }: FeedbackFormProps) {
  const { submitFeedback, submitting, error, submitted, reset } = useFeedback();
  
  const [rating, setRating] = useState<number | undefined>(undefined);
  const [comment, setComment] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [expanded, setExpanded] = useState(false);

  const toggleTag = useCallback((tag: string) => {
    setSelectedTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  }, []);

  const handleSubmit = useCallback(async () => {
    const success = await submitFeedback(taskId, {
      rating,
      comment: comment || undefined,
      tags: selectedTags.length > 0 ? selectedTags : undefined,
    });
    
    if (success && onSuccess) {
      onSuccess();
    }
  }, [taskId, rating, comment, selectedTags, submitFeedback, onSuccess]);

  const handleReset = useCallback(() => {
    reset();
    setRating(undefined);
    setComment('');
    setSelectedTags([]);
  }, [reset]);

  if (submitted) {
    return (
      <div className="p-3 bg-green-50 rounded-md border border-green-200">
        <div className="flex items-center justify-between">
          <span className="text-sm text-green-700">反馈已提交，感谢您的评价！</span>
          <Button variant="ghost" size="sm" onClick={handleReset}>
            再次提交
          </Button>
        </div>
      </div>
    );
  }

  if (!expanded) {
    return (
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setExpanded(true)}
        className="w-full"
      >
        提交反馈
      </Button>
    );
  }

  return (
    <div className="p-3 bg-gray-50 rounded-md border border-gray-200 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">提交反馈</span>
        <Button variant="ghost" size="sm" onClick={() => setExpanded(false)}>
          取消
        </Button>
      </div>

      {/* 评分 */}
      <div>
        <label className="text-xs text-gray-500 block mb-1">评分（可选）</label>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((value) => (
            <button
              key={value}
              type="button"
              onClick={() => setRating(value)}
              className={`px-2 py-1 text-sm rounded transition-colors ${
                rating === value
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
              }`}
            >
              {value}
            </button>
          ))}
        </div>
        {rating !== undefined && (
          <p className="text-xs text-gray-500 mt-1">{RATING_LABELS[rating - 1]}</p>
        )}
      </div>

      {/* 标签 */}
      <div>
        <label className="text-xs text-gray-500 block mb-1">标签（可选）</label>
        <div className="flex flex-wrap gap-1">
          {PRESET_TAGS.map((tag) => (
            <button
              key={tag}
              type="button"
              onClick={() => toggleTag(tag)}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                selectedTags.includes(tag)
                  ? 'bg-blue-100 text-blue-700 border border-blue-300'
                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* 评论 */}
      <div>
        <label className="text-xs text-gray-500 block mb-1">评论（可选）</label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="请输入您的反馈..."
          className="w-full px-2 py-1 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
          rows={2}
          maxLength={500}
        />
        <p className="text-xs text-gray-400 text-right">{comment.length}/500</p>
      </div>

      {/* 错误提示 */}
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      {/* 提交按钮 */}
      <Button
        variant="primary"
        size="sm"
        onClick={handleSubmit}
        disabled={submitting}
        className="w-full"
      >
        {submitting ? '提交中...' : '提交反馈'}
      </Button>
    </div>
  );
}