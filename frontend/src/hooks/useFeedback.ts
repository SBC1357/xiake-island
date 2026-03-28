/**
 * useFeedback Hook
 *
 * 提交任务反馈的 Hook
 */

import { useState, useCallback } from 'react';
import { API_BASE_URL } from '../api/client';

export interface FeedbackData {
  rating?: number;
  comment?: string;
  tags?: string[];
}

export interface UseFeedbackReturn {
  /** 提交反馈 */
  submitFeedback: (taskId: string, data: FeedbackData) => Promise<boolean>;
  /** 是否正在提交 */
  submitting: boolean;
  /** 错误信息 */
  error: string | null;
  /** 是否已提交 */
  submitted: boolean;
  /** 重置状态 */
  reset: () => void;
}

export function useFeedback(): UseFeedbackReturn {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const submitFeedback = useCallback(async (taskId: string, data: FeedbackData): Promise<boolean> => {
    setSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/v1/tasks/${taskId}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: '提交失败' }));
        throw new Error(errorData.detail || '提交失败');
      }

      setSubmitted(true);
      return true;
    } catch (e) {
      const message = e instanceof Error ? e.message : '提交失败';
      setError(message);
      return false;
    } finally {
      setSubmitting(false);
    }
  }, []);

  const reset = useCallback(() => {
    setSubmitting(false);
    setError(null);
    setSubmitted(false);
  }, []);

  return {
    submitFeedback,
    submitting,
    error,
    submitted,
    reset,
  };
}
