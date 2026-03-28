/**
 * Workflow Route Picker
 * 
 * 工作流路由选择器 - 选择和配置工作流执行路径
 */

import { Card, CardHeader, CardBody, Badge, Button } from './ui';
import { WORKFLOW_ROUTES, type WorkflowRoute } from '../types';

interface WorkflowRoutePickerProps {
  selectedRoute?: string;
  onRouteSelect?: (routeId: string) => void;
  disabled?: boolean;
}

export function WorkflowRoutePicker({
  selectedRoute,
  onRouteSelect,
  disabled = false,
}: WorkflowRoutePickerProps) {
  const handleSelect = (routeId: string) => {
    onRouteSelect?.(routeId);
  };

  const getPhaseBadgeVariant = (phase: WorkflowRoute['phase']) => {
    switch (phase) {
      case '一期':
        return 'success';
      case '二期':
        return 'warning';
      case '三期':
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900">工作流选择</h3>
        </div>
      </CardHeader>
      <CardBody className="space-y-3">
        <p className="text-xs text-gray-500">
          选择要执行的工作流路径
        </p>

        <div className="space-y-2">
          {WORKFLOW_ROUTES.map((route) => {
            const isSelected = selectedRoute === route.id;
            const isDisabled = disabled || route.phase !== '一期';

            return (
              <div
                key={route.id}
                className={`p-3 border rounded cursor-pointer transition-colors ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : isDisabled
                    ? 'border-gray-100 bg-gray-50 opacity-50 cursor-not-allowed'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => !isDisabled && handleSelect(route.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-900">{route.name}</span>
                      <Badge variant={getPhaseBadgeVariant(route.phase)} size="sm">
                        {route.phase}
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{route.description}</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {route.modules.map((module) => (
                        <Badge key={module} variant="default" size="sm">
                          {module}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  {isSelected && (
                    <Badge variant="info" size="sm">
                      已选
                    </Badge>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {selectedRoute && (
          <div className="pt-2 border-t">
            <Button className="w-full" disabled={disabled}>
              执行工作流
            </Button>
          </div>
        )}
      </CardBody>
    </Card>
  );
}