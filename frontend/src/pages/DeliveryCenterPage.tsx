/**
 * Delivery Center Page — 交付中心
 * 
 * 交付列表 + 前端本地筛选（文件类型/日期）+ 下载区
 */

import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardBody, Button, Select, Input, Badge, Spinner } from '../components/ui';
import { getDeliveryHistory, getArtifactUrl, type DeliveryHistoryItem } from '../api/delivery';

function getFileExtension(filename: string): string {
  const parts = filename.split('.');
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : 'unknown';
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleString('zh-CN');
}

export function DeliveryCenterPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<DeliveryHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 前端本地筛选
  const [fileTypeFilter, setFileTypeFilter] = useState('');
  const [dateFromFilter, setDateFromFilter] = useState('');
  const [dateToFilter, setDateToFilter] = useState('');

  useEffect(() => {
    setLoading(true);
    getDeliveryHistory()
      .then(res => setItems(res.items))
      .catch(e => setError(e.message || '加载交付历史失败'))
      .finally(() => setLoading(false));
  }, []);

  // 收集可用的文件类型
  const availableTypes = useMemo(() => {
    const types = new Set(items.map(i => getFileExtension(i.filename)));
    return Array.from(types).sort();
  }, [items]);

  // 应用筛选
  const filteredItems = useMemo(() => {
    return items.filter(item => {
      // 文件类型筛选
      if (fileTypeFilter && getFileExtension(item.filename) !== fileTypeFilter) {
        return false;
      }
      // 日期筛选
      if (item.created_at) {
        const itemDate = new Date(item.created_at);
        if (dateFromFilter && itemDate < new Date(dateFromFilter)) return false;
        if (dateToFilter && itemDate > new Date(dateToFilter + 'T23:59:59')) return false;
      }
      return true;
    });
  }, [items, fileTypeFilter, dateFromFilter, dateToFilter]);

  const typeFilterOptions = [
    { value: '', label: '全部类型' },
    ...availableTypes.map(t => ({ value: t, label: `.${t}` })),
  ];

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12 flex justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">交付中心</h2>
        <Button variant="ghost" size="sm" onClick={() => navigate('/')}>返回工作台</Button>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* 筛选栏 */}
      <Card>
        <CardBody>
          <div className="flex items-end gap-4">
            <div className="w-40">
              <Select
                label="文件类型"
                value={fileTypeFilter}
                onChange={e => setFileTypeFilter(e.target.value)}
                options={typeFilterOptions}
              />
            </div>
            <div className="w-40">
              <Input
                label="开始日期"
                type="date"
                value={dateFromFilter}
                onChange={e => setDateFromFilter(e.target.value)}
              />
            </div>
            <div className="w-40">
              <Input
                label="结束日期"
                type="date"
                value={dateToFilter}
                onChange={e => setDateToFilter(e.target.value)}
              />
            </div>
            {(fileTypeFilter || dateFromFilter || dateToFilter) && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setFileTypeFilter('');
                  setDateFromFilter('');
                  setDateToFilter('');
                }}
              >
                清除筛选
              </Button>
            )}
            <div className="flex-1" />
            <span className="text-sm text-gray-500">
              共 {filteredItems.length} / {items.length} 条
            </span>
          </div>
        </CardBody>
      </Card>

      {/* 交付列表 */}
      <Card>
        <CardBody className="p-0">
          {filteredItems.length === 0 ? (
            <div className="px-4 py-12 text-center text-sm text-gray-500">
              {items.length === 0 ? '暂无交付记录' : '没有匹配的记录'}
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">文件名</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 w-20">类型</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 w-44">交付时间</th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 w-24">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredItems.map((item, i) => {
                  const ext = getFileExtension(item.filename);
                  return (
                    <tr key={i} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <span className="text-gray-900">{item.filename}</span>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant="default" size="sm">.{ext}</Badge>
                      </td>
                      <td className="px-4 py-3 text-xs text-gray-500">
                        {formatDate(item.created_at)}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <a
                          href={getArtifactUrl(item.filename)}
                          download
                          className="text-blue-600 hover:underline text-xs"
                        >
                          下载
                        </a>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
