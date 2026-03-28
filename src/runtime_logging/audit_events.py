"""
Audit Events

审计事件定义，支持任务生命周期追踪和审查反馈。
"""
from typing import Optional, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field


# 审计事件类型
AuditEventType = Literal[
    "task_started",
    "task_completed",
    "task_failed",
    "workflow_requested",
    "workflow_completed",
    "workflow_failed",
    "feedback_submitted",
    "task_rerun",
    "task_viewed",
]


class AuditEvent(BaseModel):
    """
    审计事件
    
    Attributes:
        event_type: 事件类型
        timestamp: 事件时间戳 (ISO 8601)
        actor: 执行者（可选）
        details: 事件详情 (可选)
    """
    model_config = ConfigDict(extra="forbid")
    
    event_type: AuditEventType = Field(..., description="事件类型")
    timestamp: str = Field(..., description="事件时间戳")
    actor: Optional[str] = Field(default=None, description="执行者")
    details: Optional[dict] = Field(default=None, description="事件详情")


def create_audit_event(
    event_type: AuditEventType,
    actor: Optional[str] = None,
    details: Optional[dict] = None
) -> AuditEvent:
    """
    创建审计事件的便捷方法
    
    Args:
        event_type: 事件类型
        actor: 执行者 (可选)
        details: 事件详情 (可选)
        
    Returns:
        审计事件实例
    """
    return AuditEvent(
        event_type=event_type,
        timestamp=datetime.now(timezone.utc).isoformat(),
        actor=actor,
        details=details
    )


# 便捷函数
def task_started(module: str, input_hash: Optional[str] = None) -> AuditEvent:
    """创建 task_started 事件"""
    return create_audit_event(
        event_type="task_started",
        details={"module": module, "input_hash": input_hash}
    )


def task_completed(module: str, duration_ms: Optional[int] = None) -> AuditEvent:
    """创建 task_completed 事件"""
    return create_audit_event(
        event_type="task_completed",
        details={"module": module, "duration_ms": duration_ms}
    )


def task_failed(module: str, error_message: str) -> AuditEvent:
    """创建 task_failed 事件"""
    return create_audit_event(
        event_type="task_failed",
        details={"module": module, "error_message": error_message}
    )


def workflow_requested(workflow_name: str, input_summary: Optional[dict] = None) -> AuditEvent:
    """创建 workflow_requested 事件"""
    return create_audit_event(
        event_type="workflow_requested",
        details={
            "workflow_name": workflow_name,
            "input_summary": input_summary
        }
    )


def workflow_completed(
    workflow_name: str,
    task_id: str,
    child_task_ids: list[str],
    passed: bool
) -> AuditEvent:
    """创建 workflow_completed 事件"""
    return create_audit_event(
        event_type="workflow_completed",
        details={
            "workflow_name": workflow_name,
            "task_id": task_id,
            "child_task_ids": child_task_ids,
            "passed": passed
        }
    )


def workflow_failed(
    workflow_name: str,
    error_message: str,
    completed_steps: int
) -> AuditEvent:
    """创建 workflow_failed 事件"""
    return create_audit_event(
        event_type="workflow_failed",
        details={
            "workflow_name": workflow_name,
            "error_message": error_message,
            "completed_steps": completed_steps
        }
    )


def feedback_submitted(
    task_id: str,
    rating: Optional[int] = None,
    comment: Optional[str] = None,
    actor: Optional[str] = None
) -> AuditEvent:
    """创建 feedback_submitted 事件"""
    return create_audit_event(
        event_type="feedback_submitted",
        actor=actor,
        details={
            "task_id": task_id,
            "rating": rating,
            "comment": comment
        }
    )


def task_rerun(
    original_task_id: str,
    new_task_id: str,
    actor: Optional[str] = None
) -> AuditEvent:
    """创建 task_rerun 事件"""
    return create_audit_event(
        event_type="task_rerun",
        actor=actor,
        details={
            "original_task_id": original_task_id,
            "new_task_id": new_task_id
        }
    )


def task_viewed(task_id: str, actor: Optional[str] = None) -> AuditEvent:
    """创建 task_viewed 事件"""
    return create_audit_event(
        event_type="task_viewed",
        actor=actor,
        details={"task_id": task_id}
    )