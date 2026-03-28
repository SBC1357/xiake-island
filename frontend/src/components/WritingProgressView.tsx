/**
 * Writing Progress View
 * 
 * 写作进度视图 - 展示写作 Prompt 编译结果
 */

import { Card, CardHeader, CardBody, Button, Badge, Tabs, TabsList, TabsTrigger, TabsContent } from './ui';
import type { CompiledPromptResponse, PlanningResponse } from '../types';

interface WritingProgressViewProps {
  result?: CompiledPromptResponse;
  plan?: PlanningResponse;
  onWriteComplete?: () => void;
}

export function WritingProgressView({ result, plan, onWriteComplete }: WritingProgressViewProps) {
  if (!result && !plan) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900">写作进度</h3>
            <Badge variant="default">待执行</Badge>
          </div>
        </CardHeader>
        <CardBody>
          <p className="text-sm text-gray-500">请先生成规划，然后触发写作编译</p>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900">写作进度</h3>
          {result ? (
            <Badge variant="success">已完成</Badge>
          ) : (
            <Badge variant="info">进行中</Badge>
          )}
        </div>
      </CardHeader>
      <CardBody className="space-y-4">
        {/* 规划摘要 */}
        {plan && (
          <div className="p-2 bg-gray-50 rounded">
            <p className="text-xs text-gray-500 mb-1">基于规划</p>
            <p className="text-sm font-medium text-gray-900">{plan.thesis || '无核心论点'}</p>
            <p className="text-xs text-gray-500 mt-1">
              大纲 {plan.outline.length} 项 · Task: {plan.task_id.slice(0, 8)}...
            </p>
          </div>
        )}

        {/* 编译结果 */}
        {result && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Task ID</span>
              <code className="text-xs bg-gray-100 px-2 py-1 rounded">{result.task_id}</code>
            </div>

            <div className="flex items-center gap-4 text-sm">
              <span>
                System Prompt: <Badge variant="default">{result.system_prompt.length} 字符</Badge>
              </span>
              <span>
                User Prompt: <Badge variant="default">{result.user_prompt.length} 字符</Badge>
              </span>
            </div>

            {/* Prompt 详情 */}
            <Tabs defaultValue="system">
              <TabsList>
                <TabsTrigger value="system">System Prompt</TabsTrigger>
                <TabsTrigger value="user">User Prompt</TabsTrigger>
                <TabsTrigger value="config">LLM Config</TabsTrigger>
              </TabsList>

              <TabsContent value="system">
                <div className="mt-2 p-2 bg-gray-50 rounded max-h-[200px] overflow-y-auto">
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap">{result.system_prompt}</pre>
                </div>
              </TabsContent>

              <TabsContent value="user">
                <div className="mt-2 p-2 bg-gray-50 rounded max-h-[200px] overflow-y-auto">
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap">{result.user_prompt}</pre>
                </div>
              </TabsContent>

              <TabsContent value="config">
                <div className="mt-2 p-2 bg-gray-50 rounded max-h-[200px] overflow-y-auto">
                  <pre className="text-xs text-gray-700">
                    {JSON.stringify(result.llm_config, null, 2)}
                  </pre>
                </div>
              </TabsContent>
            </Tabs>

          </div>
        )}

        {onWriteComplete && (
          <div className="border-t pt-4 space-y-2">
            {!result && (
              <p className="text-xs text-gray-500">
                本步骤只生成写作指令，不直接产出正文内容。
              </p>
            )}
            <Button onClick={onWriteComplete} className="w-full">
              {result ? '重新编译写作指令' : '生成写作指令'}
            </Button>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
