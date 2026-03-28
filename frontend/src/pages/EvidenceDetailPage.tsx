/**
 * Evidence Detail Page — 证据与文献详情页
 * 
 * 文献基础信息卡 + 标签查看区 + 事实列表 + 来源锚点区
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody, Button, Badge, Spinner } from '../components/ui';
import { getFactDetail, getSources, type FactLineage, type SourceRecord } from '../api/evidence';
import { ApiError } from '../api/client';

export function EvidenceDetailPage() {
  const { factId } = useParams<{ factId: string }>();
  const navigate = useNavigate();
  const [fact, setFact] = useState<FactLineage | null>(null);
  const [sources, setSources] = useState<SourceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!factId) return;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const factDetail = await getFactDetail(factId!);
        setFact(factDetail);
        // 尝试加载来源信息
        if (factDetail.product_id) {
          try {
            const srcList = await getSources(factDetail.product_id);
            setSources(srcList);
          } catch {
            // 来源加载失败不阻塞
          }
        }
      } catch (e) {
        setError(e instanceof ApiError ? e.message : '加载事实详情失败');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [factId]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 flex justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !fact) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <p className="text-red-600 mb-4">{error || '事实不存在'}</p>
        <Button variant="secondary" onClick={() => navigate(-1)}>返回</Button>
      </div>
    );
  }

  // 从 lineage 中提取可展示的标签信息
  const lineageEntries = Object.entries(fact.lineage || {});

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">证据详情</h2>
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>返回</Button>
      </div>

      {/* 基础信息卡 */}
      <Card>
        <CardHeader>
          <h3 className="text-sm font-medium text-gray-900">事实信息</h3>
        </CardHeader>
        <CardBody className="space-y-3 text-sm">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-gray-500">事实 ID：</span>
              <span className="font-mono text-gray-700">{fact.fact_id}</span>
            </div>
            {fact.product_id && (
              <div>
                <span className="text-gray-500">产品 ID：</span>
                <span className="font-mono text-gray-700">{fact.product_id}</span>
              </div>
            )}
          </div>
        </CardBody>
      </Card>

      {/* 标签查看区 - 先读 lineage 现有字段 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900">标签与溯源</h3>
            <Badge variant="info" size="sm">只读</Badge>
          </div>
        </CardHeader>
        <CardBody>
          {lineageEntries.length > 0 ? (
            <div className="space-y-2">
              {lineageEntries.map(([key, value]) => (
                <div key={key} className="flex items-start gap-2 text-sm">
                  <Badge variant="default" size="sm">{key}</Badge>
                  <span className="text-gray-700">
                    {typeof value === 'string' ? value : JSON.stringify(value)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400">暂无标签信息</p>
          )}
        </CardBody>
      </Card>

      {/* 来源列表 */}
      <Card>
        <CardHeader>
          <h3 className="text-sm font-medium text-gray-900">
            关联来源 ({fact.sources?.length || 0})
          </h3>
        </CardHeader>
        <CardBody>
          {fact.sources && fact.sources.length > 0 ? (
            <div className="space-y-2">
              {fact.sources.map((sourceId, i) => {
                const sourceDetail = sources.find(s => s.source_id === sourceId);
                return (
                  <div key={i} className="p-2 bg-gray-50 rounded text-sm">
                    <span className="font-mono text-gray-600">{sourceId}</span>
                    {sourceDetail && (
                      <div className="mt-1 text-xs text-gray-500">
                        <span>{sourceDetail.title}</span>
                        <Badge variant="default" size="sm" className="ml-2">
                          {sourceDetail.source_type}
                        </Badge>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-gray-400">暂无来源信息</p>
          )}
        </CardBody>
      </Card>

      {/* 完整溯源数据 */}
      <Card>
        <CardHeader>
          <h3 className="text-sm font-medium text-gray-900">完整溯源数据</h3>
        </CardHeader>
        <CardBody>
          <pre className="text-xs text-gray-700 bg-gray-50 p-3 rounded overflow-x-auto max-h-60 whitespace-pre-wrap">
            {JSON.stringify(fact.lineage, null, 2)}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}
