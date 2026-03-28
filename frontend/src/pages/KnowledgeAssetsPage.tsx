/**
 * Knowledge Assets Page — 系统配置与知识资产页
 * 
 * 只读监控摘要，调用 /v1/workflow/knowledge-assets
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody, Button, Badge, Spinner } from '../components/ui';
import { getKnowledgeAssets, type KnowledgeAssetsResponse } from '../api/workflow';
import { listProducts, getEvidenceStats, type EvidenceStatsResponse } from '../api/evidence';

export function KnowledgeAssetsPage() {
  const navigate = useNavigate();
  const [assets, setAssets] = useState<KnowledgeAssetsResponse | null>(null);
  const [products, setProducts] = useState<string[]>([]);
  const [evidenceStats, setEvidenceStats] = useState<EvidenceStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [assetsRes, productsRes, statsRes] = await Promise.allSettled([
          getKnowledgeAssets(),
          listProducts(),
          getEvidenceStats(),
        ]);
        if (assetsRes.status === 'fulfilled') setAssets(assetsRes.value);
        if (productsRes.status === 'fulfilled') setProducts(productsRes.value.products);
        if (statsRes.status === 'fulfilled') setEvidenceStats(statsRes.value);
        if (assetsRes.status === 'rejected') {
          setError('无法加载知识资产数据');
        }
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 flex justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">知识资产与系统状态</h2>
        <Button variant="ghost" size="sm" onClick={() => navigate('/')}>返回工作台</Button>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {assets && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <Card>
            <CardBody className="text-center py-6">
              <p className="text-3xl font-bold text-blue-600">{assets.consumer_assets_count}</p>
              <p className="text-sm text-gray-500 mt-1">消费者资产数</p>
            </CardBody>
          </Card>
          <Card>
            <CardBody className="text-center py-6">
              <p className="text-3xl font-bold text-green-600">{assets.rules_assets_count}</p>
              <p className="text-sm text-gray-500 mt-1">规则资产数</p>
            </CardBody>
          </Card>
          <Card>
            <CardBody className="text-center py-6">
              <Badge variant={assets.has_l2 ? 'success' : 'warning'} size="sm">
                {assets.has_l2 ? 'L2 就绪' : 'L2 未就绪'}
              </Badge>
              <p className="text-sm text-gray-500 mt-2">L2 状态</p>
            </CardBody>
          </Card>
        </div>
      )}

      {/* Consumer Root */}
      {assets?.consumer_root && (
        <Card>
          <CardHeader>
            <h3 className="text-sm font-medium text-gray-900">Consumer Root</h3>
          </CardHeader>
          <CardBody>
            <code className="text-xs text-gray-700 bg-gray-50 px-2 py-1 rounded">
              {assets.consumer_root}
            </code>
          </CardBody>
        </Card>
      )}

      {/* L2 文件列表 */}
      {assets?.l2_files && assets.l2_files.length > 0 && (
        <Card>
          <CardHeader>
            <h3 className="text-sm font-medium text-gray-900">
              L2 资产文件 ({assets.l2_files.length})
            </h3>
          </CardHeader>
          <CardBody className="p-0 max-h-60 overflow-y-auto">
            <div className="divide-y divide-gray-100">
              {assets.l2_files.map((file, i) => (
                <div key={i} className="px-4 py-2 text-xs font-mono text-gray-700">
                  {file}
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* 证据数据统计 */}
      {evidenceStats && (
        <Card>
          <CardHeader>
            <h3 className="text-sm font-medium text-gray-900">证据数据统计</h3>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
              <div className="text-center py-3 bg-blue-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">{evidenceStats.total_facts}</p>
                <p className="text-xs text-gray-500 mt-1">事实条目</p>
              </div>
              <div className="text-center py-3 bg-emerald-50 rounded-lg">
                <p className="text-2xl font-bold text-emerald-600">{evidenceStats.total_sources}</p>
                <p className="text-xs text-gray-500 mt-1">来源文献</p>
              </div>
              <div className="text-center py-3 bg-purple-50 rounded-lg">
                <p className="text-2xl font-bold text-purple-600">{evidenceStats.total_products}</p>
                <p className="text-xs text-gray-500 mt-1">产品覆盖</p>
              </div>
            </div>
            {Object.keys(evidenceStats.source_type_distribution).length > 0 && (
              <div>
                <p className="text-xs text-gray-500 mb-2">来源类型分布</p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(evidenceStats.source_type_distribution).map(([type, count]) => (
                    <Badge key={type} variant="default">{type}: {count}</Badge>
                  ))}
                </div>
              </div>
            )}
          </CardBody>
        </Card>
      )}

      {/* 可用产品 */}
      <Card>
        <CardHeader>
          <h3 className="text-sm font-medium text-gray-900">
            可用产品 ({products.length})
          </h3>
        </CardHeader>
        <CardBody>
          {products.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {products.map(p => (
                <Badge key={p} variant="default">{p}</Badge>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400">暂无已注册产品</p>
          )}
        </CardBody>
      </Card>

      {/* 系统信息 */}
      <Card>
        <CardHeader>
          <h3 className="text-sm font-medium text-gray-900">系统信息</h3>
        </CardHeader>
        <CardBody className="text-sm text-gray-700 space-y-1">
          <p>系统：侠客岛写作工作台</p>
          <p>版本：一期</p>
          <p>权限策略：一期不做权限系统，所有用户按编辑角色对待</p>
        </CardBody>
      </Card>
    </div>
  );
}
