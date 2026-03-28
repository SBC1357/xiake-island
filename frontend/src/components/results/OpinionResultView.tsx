/**
 * Opinion Result View
 * 
 * 观点生成结果视图
 */

import { Card, CardHeader, CardBody, Badge } from '../ui';
import { ResultActions } from '../ui/ResultActions';
import type { OpinionGenerateResponse } from '../../types';

export interface OpinionResultViewProps {
  result: OpinionGenerateResponse;
}

export function OpinionResultView({ result }: OpinionResultViewProps) {
  const confidencePercent = Math.round(result.thesis.confidence * 100);
  
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900">核心观点</h3>
            <Badge variant={confidencePercent >= 80 ? 'success' : confidencePercent >= 50 ? 'warning' : 'danger'}>
              置信度 {confidencePercent}%
            </Badge>
          </div>
        </CardHeader>
        <CardBody>
          <p className="text-gray-800 leading-relaxed">{result.thesis.statement}</p>
          {result.thesis.evidence_refs.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="text-xs text-gray-500">引用证据：</span>
              {result.thesis.evidence_refs.map(ref => (
                <Badge key={ref} variant="info" size="sm">{ref}</Badge>
              ))}
            </div>
          )}
        </CardBody>
      </Card>
      
      {result.support_points.length > 0 && (
        <Card>
          <CardHeader>
            <h3 className="text-sm font-medium text-gray-900">支撑点</h3>
          </CardHeader>
          <CardBody className="space-y-3">
            {result.support_points.map((point, index) => (
              <div key={index} className="border-l-2 border-blue-200 pl-3">
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant={point.strength === 'strong' ? 'success' : point.strength === 'medium' ? 'warning' : 'default'} size="sm">
                    {point.strength === 'strong' ? '强' : point.strength === 'medium' ? '中' : '弱'}
                  </Badge>
                  {point.evidence_id && (
                    <span className="text-xs text-gray-500">证据: {point.evidence_id}</span>
                  )}
                </div>
                <p className="text-sm text-gray-700">{point.content}</p>
              </div>
            ))}
          </CardBody>
        </Card>
      )}
      
      {result.confidence_notes && (
        <Card>
          <CardHeader>
            <h3 className="text-sm font-medium text-gray-900">置信度说明</h3>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500 mb-2">局限性</p>
                {result.confidence_notes.limitations.length > 0 ? (
                  <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                    {result.confidence_notes.limitations.map((lim, i) => (
                      <li key={i}>{lim}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500">无</p>
                )}
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-2">假设条件</p>
                {result.confidence_notes.assumptions.length > 0 ? (
                  <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                    {result.confidence_notes.assumptions.map((asm, i) => (
                      <li key={i}>{asm}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500">无</p>
                )}
              </div>
            </div>
          </CardBody>
        </Card>
      )}
      
      <div className="text-xs text-gray-400 text-right">
        任务ID: {result.task_id}
      </div>
      
      <ResultActions
        data={result as unknown as Record<string, unknown>}
        taskId={result.task_id}
        moduleName="opinion"
      />
    </div>
  );
}