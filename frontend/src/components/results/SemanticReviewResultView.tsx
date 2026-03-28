/**
 * Semantic Review Result View
 * 
 * 语义审核结果视图
 */

import { Card, CardHeader, CardBody, Badge } from '../ui';
import { ResultActions } from '../ui/ResultActions';
import type { SemanticReviewResponse } from '../../types';

export interface SemanticReviewResultViewProps {
  result: SemanticReviewResponse;
}

const severityColors: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
  low: 'success',
  medium: 'warning',
  high: 'danger',
  critical: 'danger',
};

const severityLabels: Record<string, string> = {
  low: '低',
  medium: '中',
  high: '高',
  critical: '严重',
};

export function SemanticReviewResultView({ result }: SemanticReviewResultViewProps) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900">审核结果</h3>
            <Badge variant={result.passed ? 'success' : 'danger'}>
              {result.passed ? '通过' : '未通过'}
            </Badge>
          </div>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-green-600">{result.severity_summary.low}</p>
              <p className="text-xs text-gray-500">低</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-yellow-600">{result.severity_summary.medium}</p>
              <p className="text-xs text-gray-500">中</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-orange-600">{result.severity_summary.high}</p>
              <p className="text-xs text-gray-500">高</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-red-600">{result.severity_summary.critical}</p>
              <p className="text-xs text-gray-500">严重</p>
            </div>
          </div>
        </CardBody>
      </Card>
      
      {result.prototype_alignment && (
        <Card>
          <CardHeader>
            <h3 className="text-sm font-medium text-gray-900">原型对齐</h3>
          </CardHeader>
          <CardBody>
            <div className="flex items-center gap-4 mb-3">
              <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className={`h-full ${result.prototype_alignment.score >= 80 ? 'bg-green-500' : result.prototype_alignment.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                  style={{ width: `${result.prototype_alignment.score}%` }}
                />
              </div>
              <span className="text-sm font-medium">{result.prototype_alignment.score}分</span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500 mb-2">匹配规则</p>
                <div className="flex flex-wrap gap-1">
                  {result.prototype_alignment.matched_rules.map((rule, i) => (
                    <Badge key={i} variant="success" size="sm">{rule}</Badge>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-2">未匹配规则</p>
                <div className="flex flex-wrap gap-1">
                  {result.prototype_alignment.unmatched_rules.map((rule, i) => (
                    <Badge key={i} variant="default" size="sm">{rule}</Badge>
                  ))}
                </div>
              </div>
            </div>
            {result.prototype_alignment.notes && (
              <p className="mt-3 text-sm text-gray-600">{result.prototype_alignment.notes}</p>
            )}
          </CardBody>
        </Card>
      )}
      
      {result.findings.length > 0 && (
        <Card>
          <CardHeader>
            <h3 className="text-sm font-medium text-gray-900">发现问题 ({result.findings.length})</h3>
          </CardHeader>
          <CardBody className="space-y-3">
            {result.findings.map((finding, index) => (
              <div key={index} className="border border-gray-200 rounded-md p-3">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant={severityColors[finding.severity]} size="sm">
                    {severityLabels[finding.severity]}
                  </Badge>
                  <Badge variant="default" size="sm">{finding.category}</Badge>
                </div>
                <p className="text-sm text-gray-700">{finding.description}</p>
                {finding.suggestion && (
                  <p className="mt-1 text-sm text-blue-600">建议: {finding.suggestion}</p>
                )}
              </div>
            ))}
          </CardBody>
        </Card>
      )}
      
      {result.rewrite_target.length > 0 && (
        <Card>
          <CardHeader>
            <h3 className="text-sm font-medium text-gray-900">改写建议</h3>
          </CardHeader>
          <CardBody className="space-y-3">
            {result.rewrite_target.map((target, index) => (
              <div key={index} className="border-l-2 border-blue-400 pl-3">
                <p className="text-sm text-gray-500 line-through">{target.original}</p>
                <p className="text-sm text-gray-800">{target.suggested}</p>
                <p className="text-xs text-gray-500 mt-1">原因: {target.reason}</p>
              </div>
            ))}
          </CardBody>
        </Card>
      )}
      
      <div className="text-xs text-gray-400 text-right">
        任务ID: {result.task_id}
      </div>
      
      <ResultActions
        data={result as unknown as Record<string, unknown>}
        taskId={result.task_id}
        moduleName="semantic_review"
      />
    </div>
  );
}