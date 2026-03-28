/**
 * Delivery Panel
 * 
 * 交付面板 - 展示交付历史和下载产物
 */

import { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardBody, Button, Badge, Spinner } from './ui';
import { getDeliveryHistory, deliverContent, getArtifactUrl, ApiError } from '../api';
import type { DeliveryHistoryItem, DeliveryResult, PlanningResponse, QualityResult } from '../types';

interface DeliveryPanelProps {
  plan?: PlanningResponse;
  qualityResult?: QualityResult;
  content?: string;
  onDelivered?: (result: DeliveryResult) => void;
  disabled?: boolean;
}

export function DeliveryPanel({
  plan,
  qualityResult,
  content,
  onDelivered,
  disabled = false,
}: DeliveryPanelProps) {
  const [history, setHistory] = useState<DeliveryHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [delivering, setDelivering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deliveryResult, setDeliveryResult] = useState<DeliveryResult | null>(null);

  // 加载历史
  useEffect(() => {
    setLoading(true);
    getDeliveryHistory()
      .then((res) => setHistory(res.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const canDeliver = plan && qualityResult?.overall_status === 'passed';

  const handleDeliver = useCallback(async () => {
    if (!plan) return;

    setDelivering(true);
    setError(null);

    try {
      const result = await deliverContent({
        thesis: plan.thesis || '',
        outline: plan.outline.map((item) => ({
          title: item.title,
          type: item.type,
          domain: item.domain,
        })),
        key_evidence: plan.key_evidence,
        content,
        target_audience: plan.target_audience,
        play_id: plan.play_id,
        arc_id: plan.arc_id,
      });

      setDeliveryResult(result);
      onDelivered?.(result);

      // 刷新历史
      const historyRes = await getDeliveryHistory();
      setHistory(historyRes.items);
    } catch (e) {
      const message = e instanceof ApiError ? e.message : '交付失败';
      setError(message);
    } finally {
      setDelivering(false);
    }
  }, [plan, content, onDelivered]);

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900">交付中心</h3>
          <Badge variant="info">一期</Badge>
        </div>
      </CardHeader>
      <CardBody className="space-y-4">
        {/* 交付状态 */}
        {qualityResult && (
          <div className="p-2 bg-gray-50 rounded">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">质量审核状态</span>
              <Badge variant={qualityResult.overall_status === 'passed' ? 'success' : 'danger'}>
                {qualityResult.overall_status === 'passed' ? '可交付' : '不可交付'}
              </Badge>
            </div>
          </div>
        )}

        {/* 交付按钮 */}
        <Button
          onClick={handleDeliver}
          disabled={disabled || delivering || !canDeliver}
          className="w-full"
        >
          {delivering ? <Spinner size="sm" /> : '生成交付物'}
        </Button>

        {!canDeliver && plan && (
          <p className="text-xs text-gray-500">
            需要通过质量审核才能交付
          </p>
        )}

        {/* 错误 */}
        {error && <p className="text-sm text-red-600">{error}</p>}

        {/* 交付结果 */}
        {deliveryResult && (
          <div className="p-2 bg-green-50 border border-green-200 rounded">
            <p className="text-sm font-medium text-green-800">交付成功</p>
            <p className="text-xs text-green-600 mt-1">{deliveryResult.output_path}</p>
            <div className="mt-2 flex gap-2">
              {deliveryResult.artifacts.map((artifact) => (
                <a
                  key={artifact}
                  href={getArtifactUrl(artifact.split('/').pop() || '')}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:underline"
                >
                  下载 {artifact.split('/').pop()}
                </a>
              ))}
            </div>
          </div>
        )}

        {/* 交付历史 */}
        <div className="border-t pt-4">
          <p className="text-sm text-gray-500 mb-2">历史交付物</p>
          {loading ? (
            <div className="flex justify-center py-4">
              <Spinner />
            </div>
          ) : history.length === 0 ? (
            <p className="text-xs text-gray-400">暂无交付记录</p>
          ) : (
            <div className="max-h-[200px] overflow-y-auto space-y-2">
              {history.map((item) => (
                <div
                  key={item.path}
                  className="flex items-center justify-between p-2 bg-gray-50 rounded"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{item.filename}</p>
                    <p className="text-xs text-gray-500">{formatDate(item.created_at)}</p>
                  </div>
                  <a
                    href={getArtifactUrl(item.filename)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:underline ml-2"
                  >
                    下载
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
}