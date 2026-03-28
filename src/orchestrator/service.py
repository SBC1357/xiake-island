"""
Orchestrator Service

主编排器服务，负责接收标准化任务、判断单模块或工作流、组织调用顺序。

支持的工作流：
- article: opinion -> semantic_review（现有）
- standard_chain: Evidence -> Planning -> Writing -> Drafting -> Quality -> Delivery（标准六段链，SP-7C）
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Union, Dict, List, Optional

from src.contracts.base import TaskStatus, ModuleName
from src.runtime_logging import TaskLogger

from src.modules.opinion import (
    OpinionGenerator,
    OpinionInput,
    EvidenceBundle,
    EvidenceItem,
    OpinionOutput,
    OpinionGeneratorConfig,
)
from src.modules.semantic_review import (
    SemanticReviewer,
    SemanticReviewInput,
    SemanticReviewOutput,
    SemanticReviewerConfig,
)
from src.modules.evidence.service import EvidenceService
from src.modules.planning.service import PlanningService
from src.modules.planning.models import RouteContext, EditorialPlan
from src.modules.writing.service import WritingService
from src.modules.writing.models import CompiledPrompt
from src.modules.quality.orchestrator import QualityOrchestrator
from src.modules.quality.models import QualityResult, GateStatus
from src.modules.delivery.service import MarkdownWriter
from src.modules.delivery.models import DeliveryResult
from src.modules.drafting.service import DraftingService
from src.modules.drafting.models import (
    DraftingInput,
)
from src.adapters.llm_gateway import (
    LLMGateway,
    LLMGatewayConfig,
    FakeLLMProvider,
    create_llm_provider_from_env,
    create_llm_provider,
)

from .models import (
    ModuleTask,
    WorkflowTask,
    ModuleExecutionResult,
    OrchestratorExecutionResult,
)
from .errors import (
    OrchestratorError,
    UnsupportedModuleError,
    UnsupportedWorkflowError,
    WorkflowExecutionError,
)
from .self_check import run_self_check


class OrchestratorService:
    """
    Orchestrator 服务

    统一任务编排入口，支持：
    - 单模块调用 (opinion / semantic_review / planning / evidence / quality / delivery / drafting)
    - 工作流调用：
      - article: opinion -> semantic_review
      - standard_chain: Evidence -> Planning -> Writing -> Drafting -> Quality -> Delivery

    SP-7C: 标准链升级为六段链，Drafting 在 Writing 和 Quality 之间。

    Attributes:
        task_logger: 任务日志记录器
        opinion_generator: 观点生成器 (可选)
        semantic_reviewer: 语义审核器 (可选)
        evidence_service: 证据服务 (可选)
        planning_service: 规划服务 (可选)
        writing_service: 写作服务 (可选)
        drafting_service: 成稿服务 (可选)
        quality_orchestrator: 质量编排器 (可选)
        markdown_writer: Markdown 写入器 (可选)
    """

    def __init__(
        self,
        task_logger: TaskLogger,
        opinion_generator: OpinionGenerator | None = None,
        semantic_reviewer: SemanticReviewer | None = None,
        evidence_service: EvidenceService | None = None,
        planning_service: PlanningService | None = None,
        writing_service: WritingService | None = None,
        drafting_service: DraftingService | None = None,
        quality_orchestrator: QualityOrchestrator | None = None,
        markdown_writer: MarkdownWriter | None = None,
    ):
        """
        初始化 Orchestrator 服务

        Args:
            task_logger: 任务日志记录器
            opinion_generator: 观点生成器 (可选，默认创建)
            semantic_reviewer: 语义审核器 (可选，默认创建)
        """
        self.task_logger = task_logger

        # 初始化模块
        import os

        provider_name = os.environ.get("LLM_PROVIDER", "fake").lower()
        model_name = os.environ.get("LLM_MODEL", "fake-model")

        # 验证 provider 值
        if provider_name not in ("fake", "openai"):
            raise ValueError(
                f"Unknown LLM_PROVIDER: '{provider_name}'. "
                f"Supported values: 'fake', 'openai'."
            )

        # OpenAI 模式下验证模型名称
        if provider_name == "openai" and model_name == "fake-model":
            raise ValueError(
                "LLM_MODEL must be set to a valid OpenAI model name "
                "(e.g., 'gpt-3.5-turbo', 'gpt-4') when using OpenAI provider. "
                "Current value is the default 'fake-model'."
            )

        if opinion_generator is None:
            if provider_name == "openai":
                # 使用真实 OpenAI provider
                provider, gateway_config = create_llm_provider_from_env()
                opinion_gateway = LLMGateway(provider, gateway_config)
            else:
                # 使用 fake provider
                fake_opinion_response = json.dumps(
                    {
                        "thesis": {
                            "statement": "根据证据，该治疗方案安全有效",
                            "confidence": 0.85,
                            "evidence_refs": ["e1"],
                        },
                        "support_points": [
                            {
                                "content": "临床证据充分",
                                "strength": "strong",
                                "evidence_id": "e1",
                            }
                        ],
                        "limitations": [],
                        "assumptions": [],
                    }
                )
                opinion_gateway = LLMGateway(
                    FakeLLMProvider(response_content=fake_opinion_response),
                    LLMGatewayConfig(provider_name="fake", model_name=model_name),
                )
            self.opinion_generator = OpinionGenerator(opinion_gateway)
        else:
            self.opinion_generator = opinion_generator

        if semantic_reviewer is None:
            if provider_name == "openai":
                # 使用真实 OpenAI provider
                provider, gateway_config = create_llm_provider_from_env()
                review_gateway = LLMGateway(provider, gateway_config)
            else:
                # 使用 fake provider
                fake_review_response = json.dumps(
                    {
                        "passed": True,
                        "severity_summary": {
                            "low": 0,
                            "medium": 0,
                            "high": 0,
                            "critical": 0,
                        },
                        "findings": [],
                        "rewrite_target": [],
                        "prototype_alignment": {
                            "score": 90,
                            "matched_rules": [],
                            "unmatched_rules": [],
                            "notes": "符合要求",
                        },
                    }
                )
                review_gateway = LLMGateway(
                    FakeLLMProvider(response_content=fake_review_response),
                    LLMGatewayConfig(provider_name="fake", model_name=model_name),
                )
            config = SemanticReviewerConfig(require_prototype_alignment=True)
            self.semantic_reviewer = SemanticReviewer(review_gateway, config)
        else:
            self.semantic_reviewer = semantic_reviewer

        # 初始化新模块服务
        if evidence_service is None:
            self.evidence_service = EvidenceService()
        else:
            self.evidence_service = evidence_service

        if planning_service is None:
            self.planning_service = PlanningService()
        else:
            self.planning_service = planning_service

        if writing_service is None:
            self.writing_service = WritingService()
        else:
            self.writing_service = writing_service

        if quality_orchestrator is None:
            self.quality_orchestrator = QualityOrchestrator()
        else:
            self.quality_orchestrator = quality_orchestrator

        if markdown_writer is None:
            self.markdown_writer = MarkdownWriter()
        else:
            self.markdown_writer = markdown_writer

        # SP-7C: 初始化 Drafting 服务
        if drafting_service is None:
            # 根据环境变量决定使用 Fake 还是 OpenAI 模式
            drafting_mode = os.environ.get("DRAFTING_MODE", "fake").lower()
            
            if drafting_mode == "openai":
                # OpenAI 模式：需要配置 LLM Gateway
                from src.adapters.llm_gateway import create_llm_provider
                
                gateway_config = LLMGatewayConfig(
                    provider_name="openai",
                    model_name=os.environ.get("LLM_MODEL", "gpt-4"),
                    api_key=os.environ.get("OPENAI_API_KEY"),
                    base_url=os.environ.get("OPENAI_BASE_URL"),
                    timeout_seconds=120,
                    max_retries=3,
                )
                llm_provider = create_llm_provider(gateway_config)
                llm_gateway = LLMGateway(llm_provider, gateway_config)
                self.drafting_service = DraftingService(
                    llm_gateway=llm_gateway,
                    default_mode="openai"
                )
                print(f"[Orchestrator] DraftingService initialized in OPENAI mode (model: {gateway_config.model_name})")
            else:
                # Fake 模式：默认，生成模板内容
                self.drafting_service = DraftingService()
                print("[Orchestrator] DraftingService initialized in FAKE mode (template content)")
        else:
            self.drafting_service = drafting_service

    def execute(
        self, task: Union[ModuleTask, WorkflowTask]
    ) -> OrchestratorExecutionResult:
        """
        执行任务

        统一入口，根据任务类型路由到单模块或工作流执行。

        Args:
            task: 任务 (ModuleTask 或 WorkflowTask)

        Returns:
            执行结果

        Raises:
            UnsupportedModuleError: 不支持的模块
            UnsupportedWorkflowError: 不支持的工作流
            WorkflowExecutionError: 工作流执行失败
        """
        if isinstance(task, ModuleTask):
            return self._execute_module(task)
        elif isinstance(task, WorkflowTask):
            return self._execute_workflow(task)
        else:
            raise OrchestratorError(
                message=f"不支持的任务类型: {type(task)}",
                details={"task_type": str(type(task))},
            )

    def _execute_module(self, task: ModuleTask) -> OrchestratorExecutionResult:
        """
        执行单模块任务

        Args:
            task: 模块任务

        Returns:
            执行结果

        Raises:
            UnsupportedModuleError: 不支持的模块
        """
        # 开始父任务
        parent_input_data = {
            "mode": "module",
            "module_name": task.module_name,
            "input_data": task.input_data,
        }
        parent_task_id = self.task_logger.start_task(
            module=ModuleName.ORCHESTRATOR,
            input_data=parent_input_data,
            metadata={"mode": "module", "module_name": task.module_name},
        )

        try:
            if task.module_name == "opinion":
                child_task_id, result = self._execute_opinion(
                    task.input_data, parent_task_id
                )
            elif task.module_name == "semantic_review":
                child_task_id, result = self._execute_semantic_review(
                    task.input_data, parent_task_id
                )
            elif task.module_name == "evidence":
                child_task_id, result = self._execute_evidence(
                    task.input_data, parent_task_id
                )
            elif task.module_name == "planning":
                child_task_id, result = self._execute_planning(
                    task.input_data, parent_task_id
                )
            elif task.module_name == "writing":
                child_task_id, result = self._execute_writing(
                    task.input_data, parent_task_id
                )
            elif task.module_name == "quality":
                child_task_id, result = self._execute_quality(
                    task.input_data, parent_task_id
                )
            elif task.module_name == "delivery":
                child_task_id, result = self._execute_delivery(
                    task.input_data, parent_task_id
                )
            elif task.module_name == "drafting":
                child_task_id, result = self._execute_drafting(
                    task.input_data, parent_task_id
                )
            else:
                raise UnsupportedModuleError(
                    message=f"不支持的模块: {task.module_name}",
                    details={
                        "supported_modules": [
                            "opinion",
                            "semantic_review",
                            "evidence",
                            "planning",
                            "writing",
                            "drafting",
                            "quality",
                            "delivery",
                        ]
                    },
                )

            # 完成父任务
            self.task_logger.complete_task(
                task_id=parent_task_id,
                child_task_ids=[child_task_id],
                metadata={"status": "completed", "module": task.module_name},
            )

            return OrchestratorExecutionResult(
                task_id=parent_task_id,
                mode="module",
                status=TaskStatus.COMPLETED,
                module_name=task.module_name,
                result={"output": result},
                child_task_ids=[child_task_id],
                child_results=[
                    ModuleExecutionResult(
                        module_name=task.module_name,
                        task_id=child_task_id,
                        status=TaskStatus.COMPLETED,
                        result=result
                        if isinstance(result, dict)
                        else {"output": result},
                    )
                ],
            )

        except Exception as e:
            # 记录父任务失败
            self.task_logger.fail_task(task_id=parent_task_id, error_message=str(e))
            raise

    def _execute_workflow(self, task: WorkflowTask) -> OrchestratorExecutionResult:
        """
        执行工作流任务

        支持的工作流：
        - article: opinion -> semantic_review
        - standard_chain: Evidence -> Planning -> Writing -> Quality -> Delivery

        Args:
            task: 工作流任务

        Returns:
            执行结果

        Raises:
            UnsupportedWorkflowError: 不支持的工作流
            WorkflowExecutionError: 工作流执行失败
        """
        # 路由到不同工作流处理器
        if task.workflow_name == "standard_chain":
            return self._execute_standard_chain(task)
        elif task.workflow_name != "article":
            raise UnsupportedWorkflowError(
                message=f"不支持的工作流: {task.workflow_name}",
                details={"supported_workflows": ["article", "standard_chain"]},
            )

        # 开始父任务
        parent_input_data = {
            "mode": "workflow",
            "workflow_name": task.workflow_name,
            "input_data": task.input_data,
        }
        parent_task_id = self.task_logger.start_task(
            module=ModuleName.ORCHESTRATOR,
            input_data=parent_input_data,
            metadata={"mode": "workflow", "workflow_name": task.workflow_name},
        )

        # 记录审计事件: workflow_requested
        self.task_logger.save_audit_event(
            task_id=parent_task_id,
            event_type="workflow_requested",
            timestamp=datetime.now(timezone.utc).isoformat(),
            details={
                "workflow_name": task.workflow_name,
                "input_summary": {"has_opinion": "opinion" in task.input_data},
            },
        )

        child_task_ids = []
        child_results = []
        errors = []

        try:
            # 第一步：执行 opinion
            opinion_input = task.input_data.get("opinion", {})
            opinion_child_id, opinion_result = self._execute_opinion(
                opinion_input, parent_task_id
            )
            child_task_ids.append(opinion_child_id)
            child_results.append(
                ModuleExecutionResult(
                    module_name="opinion",
                    task_id=opinion_child_id,
                    status=TaskStatus.COMPLETED,
                    result={"passed": True},
                )
            )

            # 第二步：基于 opinion 输出构建 semantic_review 输入
            # 从 thesis + support_points 生成审查文本
            review_content = self._build_review_content(opinion_result)
            semantic_review_data = task.input_data.get("semantic_review", {})
            review_input = {
                "content": review_content,
                "audience": semantic_review_data.get("audience", "医学专业人士"),
                "prototype_hint": semantic_review_data.get("prototype_hint"),
                "register": semantic_review_data.get("register"),
                "context_metadata": semantic_review_data.get("context_metadata"),
            }

            review_child_id, review_result = self._execute_semantic_review(
                review_input, parent_task_id
            )
            child_task_ids.append(review_child_id)

            # 构建 semantic_review 的完整结果，包含 prototype_alignment 和三层输出
            semantic_review_result: dict[str, Any] = {"passed": review_result.passed}
            if review_result.prototype_alignment:
                semantic_review_result["prototype_alignment"] = {
                    "score": review_result.prototype_alignment.score,
                    "matched_rules": review_result.prototype_alignment.matched_rules,
                    "unmatched_rules": review_result.prototype_alignment.unmatched_rules,
                    "notes": review_result.prototype_alignment.notes,
                }
            # SP-6 Batch 6C: 添加三层输出和重跑范围
            if review_result.rule_layer_output:
                semantic_review_result["rule_layer_output"] = (
                    review_result.rule_layer_output
                )
            if review_result.model_review_output:
                semantic_review_result["model_review_output"] = (
                    review_result.model_review_output
                )
            if review_result.rewrite_layer_output:
                semantic_review_result["rewrite_layer_output"] = (
                    review_result.rewrite_layer_output
                )
            if review_result.rerun_scope:
                semantic_review_result["rerun_scope"] = review_result.rerun_scope

            child_results.append(
                ModuleExecutionResult(
                    module_name="semantic_review",
                    task_id=review_child_id,
                    status=TaskStatus.COMPLETED,
                    result=semantic_review_result,
                )
            )

            # 完成父任务
            self.task_logger.complete_task(
                task_id=parent_task_id,
                child_task_ids=child_task_ids,
                metadata={
                    "workflow": "article",
                    "steps_completed": 2,
                    "opinion_passed": True,
                    "review_passed": review_result.passed,
                    "prototype_alignment_score": review_result.prototype_alignment.score
                    if review_result.prototype_alignment
                    else None,
                },
            )

            # 构建最终结果，包含 prototype_alignment 和三层输出
            final_result: dict[str, Any] = {
                "opinion": {"passed": True},
                "semantic_review": {"passed": review_result.passed},
            }
            if review_result.prototype_alignment:
                final_result["prototype_alignment"] = {
                    "score": review_result.prototype_alignment.score,
                    "matched_rules": review_result.prototype_alignment.matched_rules,
                    "unmatched_rules": review_result.prototype_alignment.unmatched_rules,
                    "notes": review_result.prototype_alignment.notes,
                }
            # SP-6 Batch 6C: 添加三层输出和重跑范围到最终结果
            if review_result.rule_layer_output:
                final_result["rule_layer_output"] = review_result.rule_layer_output
            if review_result.model_review_output:
                final_result["model_review_output"] = review_result.model_review_output
            if review_result.rewrite_layer_output:
                final_result["rewrite_layer_output"] = (
                    review_result.rewrite_layer_output
                )
            if review_result.rerun_scope:
                final_result["rerun_scope"] = review_result.rerun_scope

            # 记录审计事件: workflow_completed
            self.task_logger.save_audit_event(
                task_id=parent_task_id,
                event_type="workflow_completed",
                timestamp=datetime.now(timezone.utc).isoformat(),
                details={
                    "workflow_name": task.workflow_name,
                    "task_id": parent_task_id,
                    "child_task_ids": child_task_ids,
                    "passed": review_result.passed,
                },
            )

            # 构建执行结果
            execution_result = OrchestratorExecutionResult(
                task_id=parent_task_id,
                mode="workflow",
                status=TaskStatus.COMPLETED,
                workflow_name=task.workflow_name,
                result=final_result,
                child_task_ids=child_task_ids,
                child_results=child_results,
                errors=errors,
            )

            # 执行自检
            self_check_result = run_self_check(execution_result, self.task_logger)

            # 将自检结果写入任务元数据
            entry = self.task_logger.get_task(parent_task_id)
            if entry:
                merged_metadata = entry.metadata or {}
                merged_metadata["self_check"] = {
                    "passed": self_check_result.passed,
                    "checks": self_check_result.checks,
                    "issues": self_check_result.issues,
                }
                self.task_logger.complete_task(
                    task_id=parent_task_id, metadata=merged_metadata
                )

            # 自检门：如果自检失败，将结果状态改为 FAILED 并添加错误
            if not self_check_result.passed:
                # 更新执行结果为失败
                execution_result = OrchestratorExecutionResult(
                    task_id=parent_task_id,
                    mode="workflow",
                    status=TaskStatus.FAILED,
                    workflow_name=task.workflow_name,
                    result=final_result,
                    child_task_ids=child_task_ids,
                    child_results=child_results,
                    errors=errors + self_check_result.issues,
                )

                # 更新任务日志状态为失败
                self.task_logger.fail_task(
                    task_id=parent_task_id,
                    error_message=f"Self-check failed: {', '.join(self_check_result.issues)}",
                )

            return execution_result

        except Exception as e:
            # 记录审计事件: workflow_failed
            self.task_logger.save_audit_event(
                task_id=parent_task_id,
                event_type="workflow_failed",
                timestamp=datetime.now(timezone.utc).isoformat(),
                details={
                    "workflow_name": task.workflow_name,
                    "error_message": str(e),
                    "completed_steps": len(child_results),
                },
            )

            # 记录父任务失败
            self.task_logger.fail_task(task_id=parent_task_id, error_message=str(e))
            raise WorkflowExecutionError(
                message=f"工作流执行失败: {str(e)}",
                details={
                    "workflow": task.workflow_name,
                    "completed_steps": len(child_results),
                },
            ) from e

    def _execute_opinion(
        self, input_data: dict[str, Any], parent_task_id: str
    ) -> tuple[str, OpinionOutput]:
        """
        执行 opinion 模块

        Args:
            input_data: 输入数据
            parent_task_id: 父任务ID

        Returns:
            (子任务ID, Opinion 输出)
        """
        # 修复 Finding 1: 支持正式 evidence_bundle 结构
        evidence_items = []

        # 优先使用正式的 evidence_bundle 结构
        if "evidence_bundle" in input_data:
            evidence_bundle_data = input_data["evidence_bundle"]
            if isinstance(evidence_bundle_data, dict):
                # 从 evidence_bundle.items 读取
                items_data = evidence_bundle_data.get("items", [])
                for e in items_data:
                    evidence_items.append(
                        EvidenceItem(
                            id=e.get("id", "unknown"),
                            content=e.get("content", ""),
                            source=e.get("source"),
                            relevance=e.get("relevance"),
                        )
                    )
        elif "evidence" in input_data:
            # 兼容简化写法
            for e in input_data.get("evidence", []):
                evidence_items.append(
                    EvidenceItem(
                        id=e.get("id", "unknown"), content=e.get("content", "")
                    )
                )

        # 如果没有证据，使用默认
        if not evidence_items:
            evidence_items = [EvidenceItem(id="e1", content="默认证据")]

        evidence_bundle = EvidenceBundle(
            items=evidence_items,
            summary=input_data.get("evidence_bundle", {}).get("summary")
            if isinstance(input_data.get("evidence_bundle"), dict)
            else None,
        )

        opinion_input = OpinionInput(
            evidence_bundle=evidence_bundle,
            audience=input_data.get("audience", "医学专业人士"),
            thesis_hint=input_data.get("thesis_hint"),
            context_metadata=input_data.get("context_metadata"),
        )

        # 修复 Finding 2: 显式创建 child task
        child_task_id = self.task_logger.start_task(
            module=ModuleName.OPINION,
            input_data=input_data,
            parent_task_id=parent_task_id,
            metadata={"input_summary": f"evidence_count={len(evidence_items)}"},
        )

        try:
            result = self.opinion_generator.generate(opinion_input)

            # 构建输出数据用于日志记录
            output_data = {
                "thesis": {
                    "statement": result.thesis.statement if result.thesis else None,
                    "confidence": result.thesis.confidence if result.thesis else None,
                    "evidence_refs": result.thesis.evidence_refs
                    if result.thesis
                    else [],
                },
                "support_points": [
                    {
                        "content": sp.content,
                        "strength": sp.strength,
                        "evidence_id": sp.evidence_id,
                    }
                    for sp in result.support_points
                ],
                "confidence_notes": {
                    "overall_confidence": result.confidence_notes.overall_confidence
                    if result.confidence_notes
                    else None,
                    "limitations": result.confidence_notes.limitations
                    if result.confidence_notes
                    else [],
                    "assumptions": result.confidence_notes.assumptions
                    if result.confidence_notes
                    else [],
                }
                if result.confidence_notes
                else None,
            }

            self.task_logger.complete_task(
                task_id=child_task_id,
                output_data=output_data,
                metadata={
                    "status": "completed",
                    "thesis_confidence": result.thesis.confidence
                    if result.thesis
                    else None,
                },
            )
            return child_task_id, result
        except Exception as e:
            self.task_logger.fail_task(task_id=child_task_id, error_message=str(e))
            raise

    def _execute_semantic_review(
        self, input_data: dict[str, Any], parent_task_id: str
    ) -> tuple[str, SemanticReviewOutput]:
        """
        执行 semantic_review 模块

        Args:
            input_data: 输入数据
            parent_task_id: 父任务ID

        Returns:
            (子任务ID, Semantic Review 输出)
        """
        # 修复 Finding 1: 透传所有字段，包括 register 和 context_metadata
        review_input = SemanticReviewInput(
            content=input_data.get("content", "默认内容"),
            audience=input_data.get("audience", "医学专业人士"),
            prototype_hint=input_data.get("prototype_hint"),
            register=input_data.get("register"),
            context_metadata=input_data.get("context_metadata"),
        )

        # 修复 Finding 2: 显式创建 child task
        child_task_id = self.task_logger.start_task(
            module=ModuleName.SEMANTIC_REVIEW,
            input_data=input_data,
            parent_task_id=parent_task_id,
            metadata={"content_length": len(review_input.content)},
        )

        try:
            result = self.semantic_reviewer.review(review_input)

            # 构建输出数据用于日志记录
            output_data = {
                "passed": result.passed,
                "severity_summary": {
                    "low": result.severity_summary.low,
                    "medium": result.severity_summary.medium,
                    "high": result.severity_summary.high,
                    "critical": result.severity_summary.critical,
                },
                "findings": [
                    {
                        "severity": f.severity,
                        "category": f.category,
                        "description": f.description,
                        "location": f.location,
                        "suggestion": f.suggestion,
                    }
                    for f in result.findings
                ],
                "rewrite_target": [
                    {
                        "original": rt.original,
                        "suggested": rt.suggested,
                        "reason": rt.reason,
                        "priority": rt.priority,
                    }
                    for rt in result.rewrite_target
                ],
                "prototype_alignment": {
                    "score": result.prototype_alignment.score,
                    "matched_rules": result.prototype_alignment.matched_rules,
                    "unmatched_rules": result.prototype_alignment.unmatched_rules,
                    "notes": result.prototype_alignment.notes,
                }
                if result.prototype_alignment
                else None,
                # SP-6 Batch 6C: 三层输出和重跑范围
                "rule_layer_output": result.rule_layer_output,
                "model_review_output": result.model_review_output,
                "rewrite_layer_output": result.rewrite_layer_output,
                "rerun_scope": result.rerun_scope,
            }

            self.task_logger.complete_task(
                task_id=child_task_id,
                output_data=output_data,
                metadata={"status": "completed", "passed": result.passed},
            )
            return child_task_id, result
        except Exception as e:
            self.task_logger.fail_task(task_id=child_task_id, error_message=str(e))
            raise

    def _execute_evidence(
        self, input_data: dict[str, Any], parent_task_id: str
    ) -> tuple[str, dict[str, Any]]:
        """
        执行 evidence 模块

        Args:
            input_data: 输入数据
            parent_task_id: 父任务ID

        Returns:
            (子任务ID, 证据查询结果)
        """
        child_task_id = self.task_logger.start_task(
            module=ModuleName.EVIDENCE,
            input_data=input_data,
            parent_task_id=parent_task_id,
            metadata={"product_id": input_data.get("product_id")},
        )

        try:
            product_id = input_data.get("product_id", "")
            domain = input_data.get("domain")

            facts = self.evidence_service.resolve_facts(
                {
                    "product_id": product_id,
                    "domain": domain,
                    "limit": input_data.get("limit", 20),
                }
            )

            result = {
                "fact_count": len(facts),
                "facts": [
                    {
                        "fact_id": f.fact_id,
                        "domain": f.domain,
                        "fact_key": f.fact_key,
                        "value": str(f.value) if f.value else None,
                    }
                    for f in facts[:10]  # 只返回前10条
                ],
            }

            self.task_logger.complete_task(
                task_id=child_task_id,
                output_data={"fact_count": len(facts)},
                metadata={"status": "completed"},
            )
            return child_task_id, result
        except Exception as e:
            self.task_logger.fail_task(task_id=child_task_id, error_message=str(e))
            raise

    def _execute_planning(
        self, input_data: dict[str, Any], parent_task_id: str
    ) -> tuple[str, dict[str, Any]]:
        """
        执行 planning 模块

        Args:
            input_data: 输入数据
            parent_task_id: 父任务ID

        Returns:
            (子任务ID, 规划结果)
        """
        child_task_id = self.task_logger.start_task(
            module=ModuleName.PLANNING,
            input_data=input_data,
            parent_task_id=parent_task_id,
            metadata={"product_id": input_data.get("product_id")},
        )

        try:
            context = RouteContext(
                product_id=input_data.get("product_id", ""),
                register=input_data.get("register", "R2"),
                audience=input_data.get("audience", "医学专业人士"),
                project_name=input_data.get("project_name"),
            )

            plan = self.planning_service.plan(
                context=context,
                evidence_facts=input_data.get("evidence_facts"),
                selected_facts=input_data.get("selected_facts"),
            )

            result = {
                "thesis": plan.thesis,
                "outline": plan.outline,
                "play_id": plan.play_id,
                "arc_id": plan.arc_id,
                "target_audience": plan.target_audience,
            }

            self.task_logger.complete_task(
                task_id=child_task_id,
                output_data={"thesis": plan.thesis[:50] if plan.thesis else ""},
                metadata={"status": "completed"},
            )
            return child_task_id, result
        except Exception as e:
            self.task_logger.fail_task(task_id=child_task_id, error_message=str(e))
            raise

    def _execute_writing(
        self, input_data: dict[str, Any], parent_task_id: str
    ) -> tuple[str, dict[str, Any]]:
        """
        执行 writing 模块

        Args:
            input_data: 输入数据
            parent_task_id: 父任务ID

        Returns:
            (子任务ID, 写作编译结果)
        """
        child_task_id = self.task_logger.start_task(
            module=ModuleName.WRITING,
            input_data=input_data,
            parent_task_id=parent_task_id,
            metadata={"thesis_length": len(input_data.get("thesis", ""))},
        )

        try:
            prompt = self.writing_service.compile_with_evidence(
                thesis=input_data.get("thesis", ""),
                outline=input_data.get("outline", []),
                evidence_facts=input_data.get("evidence_facts", []),
                play_id=input_data.get("play_id"),
                arc_id=input_data.get("arc_id"),
                target_audience=input_data.get("target_audience"),
                style_notes=input_data.get("style_notes"),
            )

            result = {
                "system_prompt": prompt.system_prompt,
                "user_prompt": prompt.user_prompt,
                "prompt_length": len(prompt.user_prompt),
            }

            self.task_logger.complete_task(
                task_id=child_task_id,
                output_data={"prompt_length": len(prompt.user_prompt)},
                metadata={"status": "completed"},
            )
            return child_task_id, result
        except Exception as e:
            self.task_logger.fail_task(task_id=child_task_id, error_message=str(e))
            raise

    def _execute_quality(
        self, input_data: dict[str, Any], parent_task_id: str
    ) -> tuple[str, dict[str, Any]]:
        """
        执行 quality 模块

        Args:
            input_data: 输入数据
            parent_task_id: 父任务ID

        Returns:
            (子任务ID, 质量检查结果)
        """
        child_task_id = self.task_logger.start_task(
            module=ModuleName.QUALITY,
            input_data=input_data,
            parent_task_id=parent_task_id,
            metadata={"content_length": len(input_data.get("content", ""))},
        )

        try:
            from src.modules.writing.models import CompiledPrompt

            # 支持直接传入 CompiledPrompt 或内容字符串
            content = input_data.get("content", "")
            if isinstance(content, dict):
                # 从 dict 构建 CompiledPrompt
                prompt = CompiledPrompt(
                    system_prompt=content.get("system_prompt", ""),
                    user_prompt=content.get("user_prompt", ""),
                    model_config=content.get("model_config", {}),
                    metadata=content.get("metadata", {}),
                )
                quality_result = self.quality_orchestrator.run_gates(prompt)
            else:
                quality_result = self.quality_orchestrator.run_gates_on_content(content)

            result = {
                "overall_status": quality_result.overall_status.value,
                "gates_passed": quality_result.gates_passed,
                "warnings": quality_result.warnings,
                "errors": quality_result.errors,
            }

            self.task_logger.complete_task(
                task_id=child_task_id,
                output_data={"overall_status": quality_result.overall_status.value},
                metadata={"status": "completed"},
            )
            return child_task_id, result
        except Exception as e:
            self.task_logger.fail_task(task_id=child_task_id, error_message=str(e))
            raise

    def _execute_delivery(
        self, input_data: dict[str, Any], parent_task_id: str
    ) -> tuple[str, dict[str, Any]]:
        """
        执行 delivery 模块

        Args:
            input_data: 输入数据
            parent_task_id: 父任务ID

        Returns:
            (子任务ID, 交付结果)
        """
        child_task_id = self.task_logger.start_task(
            module=ModuleName.DELIVERY,
            input_data=input_data,
            parent_task_id=parent_task_id,
            metadata={"thesis_length": len(input_data.get("thesis", ""))},
        )

        try:
            delivery_result = self.markdown_writer.create_delivery_result(
                thesis=input_data.get("thesis", ""),
                outline=input_data.get("outline", []),
                key_evidence=input_data.get("key_evidence"),
                content=input_data.get("content"),
                target_audience=input_data.get("target_audience"),
                play_id=input_data.get("play_id"),
                arc_id=input_data.get("arc_id"),
            )

            result = {
                "output_path": str(delivery_result.output_path),
                "summary": delivery_result.summary,
                "artifacts": [str(a) for a in delivery_result.artifacts],
            }

            self.task_logger.complete_task(
                task_id=child_task_id,
                output_data={"output_path": str(delivery_result.output_path)},
                metadata={"status": "completed"},
            )
            return child_task_id, result
        except Exception as e:
            self.task_logger.fail_task(task_id=child_task_id, error_message=str(e))
            raise

    def _execute_drafting(
        self, input_data: dict[str, Any], parent_task_id: str
    ) -> tuple[str, dict[str, Any]]:
        """
        执行 drafting 模块

        SP-7C: 独立成稿步骤，从 CompiledPrompt 生成正文内容。

        Args:
            input_data: 输入数据，包含 system_prompt, user_prompt, model_config 等
            parent_task_id: 父任务ID

        Returns:
            (子任务ID, 成稿结果)
        """
        child_task_id = self.task_logger.start_task(
            module=ModuleName.DRAFTING,
            input_data=input_data,
            parent_task_id=parent_task_id,
            metadata={"prompt_length": len(input_data.get("user_prompt", ""))},
        )

        try:
            drafting_input = DraftingInput(
                system_prompt=input_data.get("system_prompt", ""),
                user_prompt=input_data.get("user_prompt", ""),
                model_config=input_data.get("model_config", {}),
                target_word_count=input_data.get("target_word_count"),
                metadata=input_data.get("metadata", {}),
            )

            drafting_result = self.drafting_service.generate(drafting_input)

            result = {
                "content": drafting_result.content,
                "word_count": drafting_result.word_count,
                "trace": drafting_result.trace.to_dict(),
            }

            self.task_logger.complete_task(
                task_id=child_task_id,
                output_data={"word_count": drafting_result.word_count},
                metadata={"status": "completed"},
            )
            return child_task_id, result
        except Exception as e:
            self.task_logger.fail_task(task_id=child_task_id, error_message=str(e))
            raise

    def _execute_standard_chain(
        self, task: WorkflowTask
    ) -> OrchestratorExecutionResult:
        """
        执行标准六段链工作流：Evidence -> Planning -> Writing -> Drafting -> Quality -> Delivery

        SP-7C: 升级为六段链，Drafting 在 Writing 和 Quality 之间。
        Quality 审查的是 drafting_result.content（正文），而非 compiled_prompt。
        Delivery 接收 drafting_result.content 作为正文内容。

        Args:
            task: 工作流任务

        Returns:
            执行结果
        """
        # 开始父任务
        parent_input_data = {
            "mode": "workflow",
            "workflow_name": "standard_chain",
            "input_data": task.input_data,
        }
        parent_task_id = self.task_logger.start_task(
            module=ModuleName.ORCHESTRATOR,
            input_data=parent_input_data,
            metadata={"mode": "workflow", "workflow_name": "standard_chain"},
        )

        self.task_logger.save_audit_event(
            task_id=parent_task_id,
            event_type="workflow_requested",
            timestamp=datetime.now(timezone.utc).isoformat(),
            details={
                "workflow_name": "standard_chain",
                "input_summary": {
                    "product_id": task.input_data.get("product_id", "unknown")
                },
            },
        )

        child_task_ids = []
        child_results = []
        errors = []

        try:
            # Step 1: Evidence - 查询证据 (SP-6 Batch 6A: 使用 resolve_facts_with_trace)
            product_id = task.input_data.get("product_id", "")
            domain = task.input_data.get("domain")

            evidence_child_id = self.task_logger.start_task(
                module=ModuleName.EVIDENCE,
                input_data={"product_id": product_id, "domain": domain},
                parent_task_id=parent_task_id,
                metadata={"step": 1},
            )
            child_task_ids.append(evidence_child_id)

            # SP-6 Batch 6A: 使用 resolve_facts_with_trace 获取完整追踪
            evidence_result = self.evidence_service.resolve_facts_with_trace(
                {"product_id": product_id, "domain": domain, "limit": 20}
            )

            facts = evidence_result.facts
            retrieval_trace = evidence_result.trace

            evidence_facts = [
                {
                    "fact_id": f.fact_id,
                    "domain": f.domain,
                    "fact_key": f.fact_key,
                    "value": str(f.value) if f.value else None,
                    "definition": f.definition,
                    "definition_zh": f.definition_zh,
                    "unit": f.unit,
                }
                for f in facts
            ]

            # SP-6 Batch 6A: 在日志中记录追踪摘要
            trace_summary = retrieval_trace.summarize()

            self.task_logger.complete_task(
                task_id=evidence_child_id,
                output_data={"fact_count": len(facts), "trace_summary": trace_summary},
                metadata={"status": "completed"},
            )

            # SP-6 Batch 6A: 在 child_results 中包含 retrieval_trace
            child_results.append(
                ModuleExecutionResult(
                    module_name="evidence",
                    task_id=evidence_child_id,
                    status=TaskStatus.COMPLETED,
                    result={
                        "fact_count": len(facts),
                        "retrieval_trace": retrieval_trace.to_dict(),
                    },
                )
            )

            # Step 2: Planning - 生成编辑计划
            planning_child_id = self.task_logger.start_task(
                module=ModuleName.PLANNING,
                input_data={"product_id": product_id},
                parent_task_id=parent_task_id,
                metadata={"step": 2},
            )
            child_task_ids.append(planning_child_id)

            context = RouteContext(
                product_id=product_id,
                register=task.input_data.get("register", "R2"),
                audience=task.input_data.get("audience", "医学专业人士"),
                project_name=task.input_data.get("project_name"),
                metadata={
                    "target_word_count": task.input_data.get("target_word_count"),
                    **(task.metadata or {}),
                },
            )

            editorial_plan = self.planning_service.plan(
                context=context, evidence_facts=evidence_facts
            )

            plan_dict = {
                "thesis": editorial_plan.thesis,
                "outline": editorial_plan.outline,
                "play_id": editorial_plan.play_id,
                "arc_id": editorial_plan.arc_id,
                "target_audience": editorial_plan.target_audience,
                "key_evidence": editorial_plan.key_evidence,
                "style_notes": editorial_plan.style_notes,
            }

            self.task_logger.complete_task(
                task_id=planning_child_id,
                output_data=plan_dict,
                metadata={"status": "completed"},
            )
            child_results.append(
                ModuleExecutionResult(
                    module_name="planning",
                    task_id=planning_child_id,
                    status=TaskStatus.COMPLETED,
                    result={
                        "thesis": editorial_plan.thesis[:50]
                        if editorial_plan.thesis
                        else ""
                    },
                )
            )

            # Step 3: Writing - 编译 Prompt
            writing_child_id = self.task_logger.start_task(
                module=ModuleName.WRITING,
                input_data={"thesis": editorial_plan.thesis},
                parent_task_id=parent_task_id,
                metadata={"step": 3},
            )
            child_task_ids.append(writing_child_id)

            # SP-6 Batch 6C: 使用 compile_with_trace 获取 writing_trace
            compiled_with_trace = self.writing_service.compile_with_trace(
                thesis=editorial_plan.thesis,
                outline=editorial_plan.outline,
                evidence_facts=evidence_facts,
                play_id=editorial_plan.play_id,
                arc_id=editorial_plan.arc_id,
                target_audience=editorial_plan.target_audience,
                style_notes=editorial_plan.style_notes,
                target_word_count=editorial_plan.target_word_count,
            )

            compiled_prompt = compiled_with_trace.prompt
            writing_trace = compiled_with_trace.trace

            self.task_logger.complete_task(
                task_id=writing_child_id,
                output_data={
                    "prompt_length": len(compiled_prompt.user_prompt),
                    "writing_trace": writing_trace.to_dict(),
                },
                metadata={"status": "completed"},
            )
            child_results.append(
                ModuleExecutionResult(
                    module_name="writing",
                    task_id=writing_child_id,
                    status=TaskStatus.COMPLETED,
                    result={
                        "prompt_length": len(compiled_prompt.user_prompt),
                        "writing_trace": writing_trace.to_dict(),
                    },
                )
            )

            # Step 4: Drafting - 成稿 (SP-7C: 从 CompiledPrompt 生成正文)
            drafting_child_id = self.task_logger.start_task(
                module=ModuleName.DRAFTING,
                input_data={
                    "system_prompt": compiled_prompt.system_prompt,
                    "user_prompt": compiled_prompt.user_prompt,
                    "model_config": compiled_prompt.model_config,
                    "target_word_count": editorial_plan.target_word_count,
                    "metadata": {
                        "play_id": editorial_plan.play_id,
                        "arc_id": editorial_plan.arc_id,
                    },
                },
                parent_task_id=parent_task_id,
                metadata={"step": 4},
            )
            child_task_ids.append(drafting_child_id)

            drafting_input = DraftingInput(
                system_prompt=compiled_prompt.system_prompt,
                user_prompt=compiled_prompt.user_prompt,
                model_config=compiled_prompt.model_config,
                target_word_count=editorial_plan.target_word_count,
                metadata={
                    "play_id": editorial_plan.play_id,
                    "arc_id": editorial_plan.arc_id,
                },
            )
            drafting_result = self.drafting_service.generate(drafting_input)

            self.task_logger.complete_task(
                task_id=drafting_child_id,
                output_data={
                    "word_count": drafting_result.word_count,
                    "content_length": len(drafting_result.content),
                },
                metadata={"status": "completed"},
            )
            child_results.append(
                ModuleExecutionResult(
                    module_name="drafting",
                    task_id=drafting_child_id,
                    status=TaskStatus.COMPLETED,
                    result={
                        "word_count": drafting_result.word_count,
                        "content_length": len(drafting_result.content),
                        "trace": drafting_result.trace.to_dict(),
                    },
                )
            )

            # Step 5: Quality - 质量门禁 (SP-7C: 审查正文而非 prompt)
            quality_child_id = self.task_logger.start_task(
                module=ModuleName.QUALITY,
                input_data={"content_length": len(drafting_result.content)},
                parent_task_id=parent_task_id,
                metadata={"step": 5},
            )
            child_task_ids.append(quality_child_id)

            # SP-7C: 使用 run_gates_on_content 审查正文
            quality_result = self.quality_orchestrator.run_gates_on_content(
                drafting_result.content
            )

            self.task_logger.complete_task(
                task_id=quality_child_id,
                output_data={"overall_status": quality_result.overall_status.value},
                metadata={"status": "completed"},
            )
            child_results.append(
                ModuleExecutionResult(
                    module_name="quality",
                    task_id=quality_child_id,
                    status=TaskStatus.COMPLETED,
                    result={"overall_status": quality_result.overall_status.value},
                )
            )

            # 质量门禁检查：如果失败，阻断 Delivery
            if quality_result.overall_status == GateStatus.FAILED:
                errors.append("Quality gate failed")
                raise WorkflowExecutionError(
                    message="质量门禁检查失败，阻断交付",
                    details={"quality_errors": quality_result.errors},
                )

            # Step 6: Delivery - 交付 (SP-7C: 接收 drafting_result.content)
            delivery_child_id = self.task_logger.start_task(
                module=ModuleName.DELIVERY,
                input_data={
                    "thesis": editorial_plan.thesis,
                    "content_length": len(drafting_result.content),
                },
                parent_task_id=parent_task_id,
                metadata={"step": 6},
            )
            child_task_ids.append(delivery_child_id)

            delivery_result = self.markdown_writer.create_delivery_result(
                thesis=editorial_plan.thesis,
                outline=editorial_plan.outline,
                key_evidence=editorial_plan.key_evidence,
                content=drafting_result.content,  # SP-7C: 从 Drafting 获取正文
                target_audience=editorial_plan.target_audience,
                play_id=editorial_plan.play_id,
                arc_id=editorial_plan.arc_id,
                target_word_count=editorial_plan.target_word_count,
            )

            self.task_logger.complete_task(
                task_id=delivery_child_id,
                output_data={"output_path": str(delivery_result.output_path)},
                metadata={"status": "completed"},
            )
            child_results.append(
                ModuleExecutionResult(
                    module_name="delivery",
                    task_id=delivery_child_id,
                    status=TaskStatus.COMPLETED,
                    result={"output_path": str(delivery_result.output_path)},
                )
            )

            # 完成父任务 (SP-6 Batch 6A: 包含 retrieval_trace; SP-6 Batch 6C: 包含 writing_trace; SP-6 Batch 6D: 包含 docx 元数据; SP-7C: 包含 drafting)
            final_result = {
                "evidence": {
                    "fact_count": len(facts),
                    "retrieval_trace": retrieval_trace.to_dict(),
                },
                "planning": {
                    "thesis": editorial_plan.thesis[:50]
                    if editorial_plan.thesis
                    else ""
                },
                "writing": {
                    "prompt_length": len(compiled_prompt.user_prompt),
                    "writing_trace": writing_trace.to_dict(),
                },
                "drafting": {  # SP-7C: 成稿结果
                    "word_count": drafting_result.word_count,
                    "content_length": len(drafting_result.content),
                    "trace": drafting_result.trace.to_dict(),
                },
                "quality": {"overall_status": quality_result.overall_status.value},
                "delivery": {
                    "output_path": str(delivery_result.output_path),
                    "markdown_preview_path": str(delivery_result.markdown_preview_path)
                    if delivery_result.markdown_preview_path
                    else None,
                    "docx_path": str(delivery_result.docx_path)
                    if delivery_result.docx_path
                    else None,
                    "final_docx_word_count": delivery_result.final_docx_word_count,
                    "word_count_basis": delivery_result.word_count_basis,
                    "target_word_count": delivery_result.target_word_count,
                    "word_count_gate_passed": delivery_result.word_count_gate_passed,
                },
            }

            self.task_logger.complete_task(
                task_id=parent_task_id,
                child_task_ids=child_task_ids,
                metadata={
                    "workflow": "standard_chain",
                    "steps_completed": 6,  # SP-7C: 六段链
                    "quality_status": quality_result.overall_status.value,
                },
            )

            self.task_logger.save_audit_event(
                task_id=parent_task_id,
                event_type="workflow_completed",
                timestamp=datetime.now(timezone.utc).isoformat(),
                details={
                    "workflow_name": "standard_chain",
                    "task_id": parent_task_id,
                    "child_task_ids": child_task_ids,
                    "passed": True,
                },
            )

            return OrchestratorExecutionResult(
                task_id=parent_task_id,
                mode="workflow",
                status=TaskStatus.COMPLETED,
                workflow_name="standard_chain",
                result=final_result,
                child_task_ids=child_task_ids,
                child_results=child_results,
                errors=errors,
            )

        except Exception as e:
            self.task_logger.save_audit_event(
                task_id=parent_task_id,
                event_type="workflow_failed",
                timestamp=datetime.now(timezone.utc).isoformat(),
                details={
                    "workflow_name": "standard_chain",
                    "error_message": str(e),
                    "completed_steps": len(child_results),
                },
            )

            self.task_logger.fail_task(task_id=parent_task_id, error_message=str(e))
            raise WorkflowExecutionError(
                message=f"标准六段链执行失败: {str(e)}",  # SP-7C: 六段链
                details={
                    "workflow": "standard_chain",
                    "completed_steps": len(child_results),
                },
            ) from e

    def _build_review_content(self, opinion_result: OpinionOutput) -> str:
        """
        基于 opinion 输出构建 semantic_review 输入内容

        Args:
            opinion_result: Opinion 输出

        Returns:
            审查文本
        """
        parts = []

        # 添加论题
        if hasattr(opinion_result, "thesis") and opinion_result.thesis:
            parts.append(f"论题: {opinion_result.thesis.statement}")
            parts.append(f"置信度: {opinion_result.thesis.confidence}")

        # 添加支撑点
        if hasattr(opinion_result, "support_points") and opinion_result.support_points:
            parts.append("\n支撑点:")
            for sp in opinion_result.support_points:
                parts.append(f"- {sp.content} (强度: {sp.strength})")

        return "\n".join(parts) if parts else "待审核内容"
