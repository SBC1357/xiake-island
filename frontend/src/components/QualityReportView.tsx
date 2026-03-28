/**
 * Quality Report View
 * 
 * 质量报告视图 - 展示质量门禁检查结果
 */

import { Card, CardHeader, CardBody, Badge } from './ui';
import type { QualityResult } from '../types';

interface QualityReportViewProps {
  result?: QualityResult;
  content?: string;
}

export function QualityReportView({ result, content }: QualityReportViewProps) {
  if (!result) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900">质量报告</h3>
            <Badge variant="default">待执行</Badge>
          </div>
        </CardHeader>
        <CardBody>
          <p className="text-sm text-gray-500">请先完成成稿，然后触发质量审核</p>
        </CardBody>
      </Card>
    );
  }

  const isPassed = result.overall_status === 'passed';

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900">质量报告</h3>
          <Badge variant={isPassed ? 'success' : 'danger'}>
            {isPassed ? '通过' : '未通过'}
          </Badge>
        </div>
      </CardHeader>
      <CardBody className="space-y-4">
        {/* 基本信息 */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">Task ID</span>
          <code className="text-xs bg-gray-100 px-2 py-1 rounded">{result.task_id.slice(0, 8)}...</code>
        </div>

        {/* 通过的门禁 */}
        {result.gates_passed.length > 0 && (
          <div>
            <p className="text-xs text-gray-500 mb-1">通过的门禁</p>
            <div className="flex flex-wrap gap-1">
              {result.gates_passed.map((gate) => (
                <Badge key={gate} variant="success" size="sm">
                  {gate}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* 警告 */}
        {result.warnings.length > 0 && (
          <div>
            <p className="text-xs text-yellow-600 mb-1">警告 ({result.warnings.length})</p>
            <ul className="space-y-1">
              {result.warnings.map((w, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm">
                  <Badge variant="warning" size="sm">
                    {w.gate}
                  </Badge>
                  <span className="text-gray-600">{w.message}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 错误 */}
        {result.errors.length > 0 && (
          <div>
            <p className="text-xs text-red-600 mb-1">错误 ({result.errors.length})</p>
            <ul className="space-y-1">
              {result.errors.map((e, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm">
                  <Badge variant="danger" size="sm">
                    {e.gate}
                  </Badge>
                  <span className="text-gray-600">{e.message}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 内容预览 */}
        {content && (
          <div>
            <p className="text-xs text-gray-500 mb-1">审核内容预览</p>
            <div className="p-2 bg-gray-50 rounded max-h-[100px] overflow-y-auto">
              <p className="text-xs text-gray-600 line-clamp-3">{content}</p>
            </div>
          </div>
        )}

        {/* 总结 */}
        <div className="p-2 bg-gray-50 rounded">
          <div className="grid grid-cols-3 gap-2 text-center text-xs">
            <div>
              <p className="text-gray-500">通过</p>
              <p className="text-lg font-medium text-green-600">{result.gates_passed.length}</p>
            </div>
            <div>
              <p className="text-gray-500">警告</p>
              <p className="text-lg font-medium text-yellow-600">{result.warnings.length}</p>
            </div>
            <div>
              <p className="text-gray-500">错误</p>
              <p className="text-lg font-medium text-red-600">{result.errors.length}</p>
            </div>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
