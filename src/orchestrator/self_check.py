"""
Internal Self-Check Gate

内部质量闸门，用于验证工作流执行结果的完整性和一致性。
这是一个内部模块，不暴露独立 API。
"""
from typing import Optional
from dataclasses import dataclass, field

from src.orchestrator.models import OrchestratorExecutionResult
from src.runtime_logging import TaskLogger


@dataclass
class SelfCheckResult:
    """
    自检结果
    
    Attributes:
        passed: 是否通过所有检查
        checks: 各项检查结果
        issues: 发现的问题列表
    """
    passed: bool = True
    checks: dict[str, bool] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    
    def add_check(self, name: str, passed: bool, issue: Optional[str] = None) -> None:
        """添加检查结果"""
        self.checks[name] = passed
        if not passed:
            self.passed = False
            if issue:
                self.issues.append(issue)


class WorkflowSelfCheck:
    """
    工作流自检器
    
    执行工作流结果的自检，确保：
    1. 结果完整性
    2. 子任务可追踪
    3. 关键字段不丢失
    4. 失败场景正确处理
    """
    
    def __init__(self, task_logger: TaskLogger):
        """
        初始化自检器
        
        Args:
            task_logger: 任务日志记录器，用于验证子任务可追踪性
        """
        self.task_logger = task_logger
    
    def check_workflow_result(self, result: OrchestratorExecutionResult) -> SelfCheckResult:
        """
        执行工作流结果自检
        
        Args:
            result: Orchestrator 执行结果
            
        Returns:
            自检结果
        """
        check_result = SelfCheckResult()
        
        # 检查 1: 工作流结果完整性
        self._check_result_completeness(result, check_result)
        
        # 检查 2: opinion 输出存在
        self._check_opinion_output(result, check_result)
        
        # 检查 3: semantic_review 输出存在
        self._check_semantic_review_output(result, check_result)
        
        # 检查 4: child_task_ids 可追踪
        self._check_child_task_traceability(result, check_result)
        
        # 检查 5: fail-fast 场景检查
        self._check_fail_fast_integrity(result, check_result)
        
        # 检查 6: prototype_alignment 未丢失
        self._check_prototype_alignment(result, check_result)
        
        return check_result
    
    def _check_result_completeness(
        self,
        result: OrchestratorExecutionResult,
        check_result: SelfCheckResult
    ) -> None:
        """检查结果完整性"""
        # task_id 存在
        has_task_id = bool(result.task_id)
        check_result.add_check(
            "task_id_exists",
            has_task_id,
            "task_id is missing or empty" if not has_task_id else None
        )
        
        # child_task_ids 存在且不为空
        has_child_ids = bool(result.child_task_ids) and len(result.child_task_ids) > 0
        check_result.add_check(
            "child_task_ids_exist",
            has_child_ids,
            "child_task_ids is missing or empty" if not has_child_ids else None
        )
        
        # result 存在
        has_result = result.result is not None
        check_result.add_check(
            "result_exists",
            has_result,
            "result is None" if not has_result else None
        )
    
    def _check_opinion_output(
        self,
        result: OrchestratorExecutionResult,
        check_result: SelfCheckResult
    ) -> None:
        """检查 opinion 输出存在"""
        opinion_exists = any(
            cr.module_name == "opinion" for cr in result.child_results
        )
        check_result.add_check(
            "opinion_output_exists",
            opinion_exists,
            "opinion output is missing from child_results" if not opinion_exists else None
        )
    
    def _check_semantic_review_output(
        self,
        result: OrchestratorExecutionResult,
        check_result: SelfCheckResult
    ) -> None:
        """检查 semantic_review 输出存在"""
        review_exists = any(
            cr.module_name == "semantic_review" for cr in result.child_results
        )
        check_result.add_check(
            "semantic_review_output_exists",
            review_exists,
            "semantic_review output is missing from child_results" if not review_exists else None
        )
    
    def _check_child_task_traceability(
        self,
        result: OrchestratorExecutionResult,
        check_result: SelfCheckResult
    ) -> None:
        """检查子任务可追踪性"""
        all_traceable = True
        untraceable_ids = []
        
        for child_id in result.child_task_ids:
            task = self.task_logger.get_task(child_id)
            if task is None:
                all_traceable = False
                untraceable_ids.append(child_id)
        
        check_result.add_check(
            "child_tasks_traceable",
            all_traceable,
            f"child_task_ids not traceable: {untraceable_ids}" if not all_traceable else None
        )
    
    def _check_fail_fast_integrity(
        self,
        result: OrchestratorExecutionResult,
        check_result: SelfCheckResult
    ) -> None:
        """
        检查 fail-fast 场景完整性
        
        如果工作流失败，验证没有伪造的后续任务
        """
        if result.status.value == "failed":
            # 失败场景：检查是否有未执行的子任务被错误标记为完成
            has_fake_completed = any(
                cr.status.value == "completed" and cr.result is None
                for cr in result.child_results
            )
            check_result.add_check(
                "no_fake_completed_tasks",
                not has_fake_completed,
                "fail-fast scenario has fake completed tasks" if has_fake_completed else None
            )
        else:
            # 成功场景：标记为通过（不适用）
            check_result.add_check("no_fake_completed_tasks", True)
    
    def _check_prototype_alignment(
        self,
        result: OrchestratorExecutionResult,
        check_result: SelfCheckResult
    ) -> None:
        """检查 prototype_alignment 未丢失"""
        # 检查顶层 result 是否包含 prototype_alignment
        has_prototype_alignment = (
            result.result is not None and
            "prototype_alignment" in result.result and
            result.result["prototype_alignment"] is not None
        )
        
        check_result.add_check(
            "prototype_alignment_not_lost",
            has_prototype_alignment,
            "prototype_alignment is missing or None in result" if not has_prototype_alignment else None
        )


def run_self_check(
    result: OrchestratorExecutionResult,
    task_logger: TaskLogger
) -> SelfCheckResult:
    """
    执行自检的便捷函数
    
    Args:
        result: Orchestrator 执行结果
        task_logger: 任务日志记录器
        
    Returns:
        自检结果
    """
    checker = WorkflowSelfCheck(task_logger)
    return checker.check_workflow_result(result)