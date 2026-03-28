"""
Tasks API Router

实现任务历史和详情查询 API 路由。
"""
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field
from fastapi import APIRouter, HTTPException, Depends, Query

from src.runtime_logging import TaskLogger, TaskLogQuery
from src.runtime_logging.hash_utils import _filter_sensitive_fields
from src.contracts.base import TaskStatus, ModuleName

# 创建 Router
router = APIRouter(prefix="/v1/tasks", tags=["tasks"])

# 导入共享的 task logger
from src.api.app import get_shared_task_logger


# ==================== 响应模型 ====================

class TaskListItemResponse(BaseModel):
    """任务列表项响应"""
    model_config = ConfigDict(extra="forbid")
    
    task_id: str = Field(..., description="任务ID")
    module: str = Field(..., description="执行模块")
    status: str = Field(..., description="任务状态")
    started_at: str = Field(..., description="开始时间 (ISO 8601)")
    completed_at: Optional[str] = Field(default=None, description="完成时间 (ISO 8601)")
    duration_ms: Optional[int] = Field(default=None, description="执行耗时 (毫秒)")
    error_message: Optional[str] = Field(default=None, description="错误信息")


class TaskListResponse(BaseModel):
    """任务列表响应"""
    model_config = ConfigDict(extra="forbid")
    
    tasks: list[TaskListItemResponse] = Field(default_factory=list, description="任务列表")
    total: int = Field(..., description="总数量")


class TaskDetailResponse(BaseModel):
    """任务详情响应"""
    model_config = ConfigDict(extra="forbid")
    
    task_id: str = Field(..., description="任务ID")
    module: str = Field(..., description="执行模块")
    status: str = Field(..., description="任务状态")
    input_hash: Optional[str] = Field(default=None, description="输入哈希")
    input_data: Optional[dict[str, Any]] = Field(default=None, description="完整输入参数")
    output_data: Optional[dict[str, Any]] = Field(default=None, description="完整输出结果")
    parent_task_id: Optional[str] = Field(default=None, description="父任务ID")
    child_task_ids: list[str] = Field(default_factory=list, description="子任务ID列表")
    started_at: str = Field(..., description="开始时间 (ISO 8601)")
    completed_at: Optional[str] = Field(default=None, description="完成时间 (ISO 8601)")
    duration_ms: Optional[int] = Field(default=None, description="执行耗时 (毫秒)")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="元数据")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    audit_events: list[dict[str, Any]] = Field(default_factory=list, description="审计事件列表")


# ==================== API 端点 ====================

@router.get("", response_model=TaskListResponse)
async def list_tasks(
    module: Optional[str] = Query(default=None, description="按模块过滤"),
    status: Optional[str] = Query(default=None, description="按状态过滤"),
    limit: int = Query(default=50, ge=1, le=200, description="返回数量限制"),
    offset: int = Query(default=0, ge=0, description="分页偏移"),
    logger: TaskLogger = Depends(get_shared_task_logger)
):
    """
    查询任务历史列表
    
    支持按模块、状态过滤，按时间倒序返回。
    
    Args:
        module: 模块名称过滤 (opinion, semantic_review, orchestrator)
        status: 状态过滤 (running, completed, failed)
        limit: 返回数量限制 (默认50，最大200)
        offset: 分页偏移
        
    Returns:
        任务列表，不包含完整输入输出（详情接口负责）
    """
    # 构建查询条件
    query_params = {"limit": limit + offset}  # 多取一些用于分页
    
    if module:
        try:
            query_params["module"] = ModuleName(module)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"无效的模块名称: {module}. 有效值: opinion, semantic_review, orchestrator"
            )
    
    if status:
        try:
            query_params["status"] = TaskStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"无效的状态: {status}. 有效值: running, completed, failed"
            )
    
    query = TaskLogQuery(**query_params)
    entries = logger.query_tasks(query)
    
    # 应用偏移
    paginated_entries = entries[offset:offset + limit]
    
    # 转换为响应模型
    task_items = [
        TaskListItemResponse(
            task_id=entry.task_id,
            module=entry.module.value,
            status=entry.status.value,
            started_at=entry.started_at,
            completed_at=entry.completed_at,
            duration_ms=entry.duration_ms,
            error_message=entry.error_message
        )
        for entry in paginated_entries
    ]
    
    return TaskListResponse(
        tasks=task_items,
        total=len(entries)  # 总匹配数量
    )


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task_detail(
    task_id: str,
    logger: TaskLogger = Depends(get_shared_task_logger)
):
    """
    获取任务详情
    
    返回完整任务信息，包括输入参数、输出结果、子任务列表和审计事件。
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务详情
        
    Raises:
        HTTPException 404: 任务不存在
    """
    entry = logger.get_task(task_id)
    
    if entry is None:
        raise HTTPException(
            status_code=404,
            detail=f"任务不存在: {task_id}"
        )
    
    # 获取审计事件
    audit_events = logger.get_audit_events(task_id)
    
    # 过滤敏感信息（保留空对象 {}）
    filtered_input_data = _filter_sensitive_fields(entry.input_data) if entry.input_data is not None else None
    filtered_output_data = _filter_sensitive_fields(entry.output_data) if entry.output_data is not None else None
    
    return TaskDetailResponse(
        task_id=entry.task_id,
        module=entry.module.value,
        status=entry.status.value,
        input_hash=entry.input_hash,
        input_data=filtered_input_data,
        output_data=filtered_output_data,
        parent_task_id=entry.parent_task_id,
        child_task_ids=entry.child_task_ids,
        started_at=entry.started_at,
        completed_at=entry.completed_at,
        duration_ms=entry.duration_ms,
        metadata=entry.metadata,
        error_message=entry.error_message,
        audit_events=audit_events
    )


# ==================== 反馈接口 ====================

class FeedbackRequest(BaseModel):
    """反馈请求"""
    model_config = ConfigDict(extra="forbid")
    
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="评分 (1-5)")
    comment: Optional[str] = Field(default=None, max_length=2000, description="评论")
    tags: list[str] = Field(default_factory=list, description="标签")


class FeedbackResponse(BaseModel):
    """反馈响应"""
    model_config = ConfigDict(extra="forbid")
    
    task_id: str = Field(..., description="任务ID")
    message: str = Field(..., description="反馈结果消息")


@router.post("/{task_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    task_id: str,
    request: FeedbackRequest,
    logger: TaskLogger = Depends(get_shared_task_logger)
):
    """
    提交任务反馈
    
    将审查反馈记录为审计事件，关联到原任务。
    
    Args:
        task_id: 任务ID
        request: 反馈请求
        
    Returns:
        反馈结果
        
    Raises:
        HTTPException 404: 任务不存在
    """
    from datetime import datetime, timezone
    
    # 检查任务是否存在
    entry = logger.get_task(task_id)
    
    if entry is None:
        raise HTTPException(
            status_code=404,
            detail=f"任务不存在: {task_id}"
        )
    
    # 保存审计事件
    logger.save_audit_event(
        task_id=task_id,
        event_type="feedback_submitted",
        timestamp=datetime.now(timezone.utc).isoformat(),
        details={
            "rating": request.rating,
            "comment": request.comment,
            "tags": request.tags
        }
    )
    
    return FeedbackResponse(
        task_id=task_id,
        message="反馈已提交"
    )


# ==================== 版本/回退接口 ====================

class TaskVersionResponse(BaseModel):
    """任务版本响应"""
    model_config = ConfigDict(extra="forbid")
    
    input_hash: str = Field(..., description="输入哈希")
    versions: list[TaskListItemResponse] = Field(default_factory=list, description="版本列表")
    total: int = Field(..., description="总数量")


class TaskCopyResponse(BaseModel):
    """任务复制响应"""
    model_config = ConfigDict(extra="forbid")
    
    new_task_id: str = Field(..., description="新任务ID")
    original_task_id: str = Field(..., description="原任务ID")
    message: str = Field(..., description="操作结果消息")


@router.get("/versions/{input_hash}", response_model=TaskVersionResponse)
async def get_task_versions(
    input_hash: str,
    limit: int = Query(default=20, ge=1, le=100, description="返回数量限制"),
    logger: TaskLogger = Depends(get_shared_task_logger)
):
    """
    按输入哈希查询任务版本
    
    返回具有相同 input_hash 的所有任务版本。
    
    Args:
        input_hash: 输入哈希
        limit: 返回数量限制
        
    Returns:
        版本列表
    """
    from src.runtime_logging import TaskLogQuery
    
    entries = logger.query_tasks(TaskLogQuery(input_hash=input_hash, limit=limit))
    
    versions = [
        TaskListItemResponse(
            task_id=entry.task_id,
            module=entry.module.value,
            status=entry.status.value,
            started_at=entry.started_at,
            completed_at=entry.completed_at,
            duration_ms=entry.duration_ms,
            error_message=entry.error_message
        )
        for entry in entries
    ]
    
    return TaskVersionResponse(
        input_hash=input_hash,
        versions=versions,
        total=len(entries)
    )


@router.post("/{task_id}/copy", response_model=TaskCopyResponse)
async def copy_task(
    task_id: str,
    logger: TaskLogger = Depends(get_shared_task_logger)
):
    """
    复制任务输入参数创建新任务记录
    
    注意：此接口仅创建新任务记录并保存原始输入参数，
    不会实际执行任务。如需执行，请通过对应的工作流 API 提交。
    
    Args:
        task_id: 原任务ID
        
    Returns:
        新任务ID
        
    Raises:
        HTTPException 404: 任务不存在
        HTTPException 400: 任务无输入数据
    """
    from datetime import datetime, timezone
    from src.runtime_logging import TaskLogQuery
    
    # 获取原任务
    entry = logger.get_task(task_id)
    
    if entry is None:
        raise HTTPException(
            status_code=404,
            detail=f"任务不存在: {task_id}"
        )
    
    if entry.input_data is None:
        raise HTTPException(
            status_code=400,
            detail="任务无输入数据，无法复制"
        )
    
    # 创建新任务记录（不执行）
    new_task_id = logger.start_task(
        module=entry.module,
        input_data=entry.input_data,
        input_hash=entry.input_hash,
        metadata={
            "copied_from": task_id,
            "copied_at": datetime.now(timezone.utc).isoformat()
        }
    )
    
    # 记录审计事件
    logger.save_audit_event(
        task_id=new_task_id,
        event_type="task_copied",
        timestamp=datetime.now(timezone.utc).isoformat(),
        details={
            "original_task_id": task_id,
            "new_task_id": new_task_id
        }
    )
    
    # 同时在原任务上记录
    logger.save_audit_event(
        task_id=task_id,
        event_type="task_copied",
        timestamp=datetime.now(timezone.utc).isoformat(),
        details={
            "original_task_id": task_id,
            "new_task_id": new_task_id
        }
    )
    
    return TaskCopyResponse(
        new_task_id=new_task_id,
        original_task_id=task_id,
        message="已创建新任务记录（未执行），请通过工作流 API 提交执行"
    )