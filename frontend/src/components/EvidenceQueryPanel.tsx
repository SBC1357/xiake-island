/**
 * Evidence Query Panel
 * 
 * 证据查询面板 - 用于查询和展示证据事实
 */

import { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardBody, Button, Input, Select, Badge, Spinner } from './ui';
import { queryEvidence, listProducts, ApiError } from '../api';
import type { FactRecord, ProductListResponse } from '../types';

interface EvidenceQueryPanelProps {
  onFactsSelected?: (facts: FactRecord[]) => void;
  disabled?: boolean;
}

const DOMAIN_OPTIONS = [
  { value: '', label: '全部领域' },
  { value: 'efficacy', label: '疗效' },
  { value: 'safety', label: '安全性' },
  { value: 'biomarker', label: '生物标志物' },
  { value: 'moa', label: '作用机制' },
];

export function EvidenceQueryPanel({ onFactsSelected, disabled = false }: EvidenceQueryPanelProps) {
  const [products, setProducts] = useState<ProductListResponse>({ products: [], count: 0 });
  const [selectedProductId, setSelectedProductId] = useState<string>('');
  const [selectedDomain, setSelectedDomain] = useState<string>('');
  const [limit, setLimit] = useState<number>(50);
  const [facts, setFacts] = useState<FactRecord[]>([]);
  const [selectedFactIds, setSelectedFactIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 加载产品列表
  useEffect(() => {
    listProducts()
      .then(setProducts)
      .catch((e) => {
        console.error('Failed to load products:', e);
      });
  }, []);

  // 查询证据
  const handleQuery = useCallback(async () => {
    if (!selectedProductId) {
      setError('请选择产品');
      return;
    }

    setLoading(true);
    setError(null);
    setFacts([]);
    setSelectedFactIds(new Set());

    try {
      const results = await queryEvidence({
        product_id: selectedProductId,
        domain: selectedDomain || undefined,
        limit,
      });
      setFacts(results);
    } catch (e) {
      const message = e instanceof ApiError ? e.message : '查询失败';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [selectedProductId, selectedDomain, limit]);

  // 选择/取消选择事实
  const toggleFactSelection = (factId: string) => {
    const newSelection = new Set(selectedFactIds);
    if (newSelection.has(factId)) {
      newSelection.delete(factId);
    } else {
      newSelection.add(factId);
    }
    setSelectedFactIds(newSelection);
  };

  // 全选/取消全选
  const toggleSelectAll = () => {
    if (selectedFactIds.size === facts.length) {
      setSelectedFactIds(new Set());
    } else {
      setSelectedFactIds(new Set(facts.map((f) => f.fact_id)));
    }
  };

  // 确认选择
  const handleConfirm = () => {
    const selectedFacts = facts.filter((f) => selectedFactIds.has(f.fact_id));
    onFactsSelected?.(selectedFacts);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900">证据查询</h3>
          <Badge variant="info">一期</Badge>
        </div>
      </CardHeader>
      <CardBody className="space-y-4">
        {/* 查询条件 */}
        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">产品</label>
            <Select
              value={selectedProductId}
              onChange={(e) => setSelectedProductId(e.target.value)}
              disabled={disabled || loading}
              options={[
                { value: '', label: '选择产品...' },
                ...products.products.map((p) => ({ value: p, label: p })),
              ]}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">领域</label>
            <Select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              disabled={disabled || loading}
              options={DOMAIN_OPTIONS}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">数量限制</label>
            <Input
              type="number"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value) || 50)}
              disabled={disabled || loading}
              min={1}
              max={1000}
            />
          </div>
        </div>

        <div className="flex gap-2">
          <Button onClick={handleQuery} disabled={disabled || loading || !selectedProductId}>
            {loading ? <Spinner size="sm" /> : '查询'}
          </Button>
        </div>

        {/* 错误信息 */}
        {error && <p className="text-sm text-red-600">{error}</p>}

        {/* 查询结果 */}
        {facts.length > 0 && (
          <div className="border-t pt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500">
                找到 {facts.length} 条证据，已选择 {selectedFactIds.size} 条
              </span>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={toggleSelectAll}>
                  {selectedFactIds.size === facts.length ? '取消全选' : '全选'}
                </Button>
                {selectedFactIds.size > 0 && (
                  <Button size="sm" onClick={handleConfirm}>
                    确认选择
                  </Button>
                )}
              </div>
            </div>

            <div className="max-h-[300px] overflow-y-auto space-y-2">
              {facts.map((fact) => (
                <div
                  key={fact.fact_id}
                  className={`p-2 border rounded cursor-pointer transition-colors ${
                    selectedFactIds.has(fact.fact_id)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => toggleFactSelection(fact.fact_id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <Badge variant="default" size="sm">
                          {fact.domain}
                        </Badge>
                        <span className="text-xs text-gray-500">{fact.fact_key}</span>
                      </div>
                      <p className="mt-1 text-sm text-gray-900 truncate">{fact.value}</p>
                      {fact.definition_zh && (
                        <p className="mt-1 text-xs text-gray-500">{fact.definition_zh}</p>
                      )}
                    </div>
                    <Badge
                      variant={fact.status === 'approved' ? 'success' : 'warning'}
                      size="sm"
                    >
                      {fact.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  );
}