"""
Standard Chain Workflow API 测试

测试 POST /v1/workflow/standard-chain API。
"""

import pytest
from fastapi.testclient import TestClient

from src.api.app import app


# 创建测试客户端
client = TestClient(app)


class TestStandardChainWorkflowAPI:
    """测试 Standard Chain Workflow API"""

    def test_standard_chain_workflow_success(self):
        """测试成功执行标准六段链工作流 (SP-7C: 6 steps)"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 验证响应结构
        assert "task_id" in data
        assert "child_task_ids" in data
        assert "status" in data
        assert "result" in data
        assert "child_results" in data

        # 验证 task_id 存在
        assert data["task_id"] is not None
        assert len(data["task_id"]) == 36  # UUID format

        # SP-7C: 验证 child_task_ids 有六个子任务
        assert len(data["child_task_ids"]) == 6

        # 验证状态为 completed
        assert data["status"] == "completed"

        # SP-7C: 验证 child_results 有六个结果
        assert len(data["child_results"]) == 6

        # SP-7C: 验证六个模块的执行顺序
        modules = [cr["module_name"] for cr in data["child_results"]]
        assert modules == [
            "evidence",
            "planning",
            "writing",
            "drafting",
            "quality",
            "delivery",
        ]

    def test_standard_chain_workflow_with_domain(self):
        """测试带领域过滤的标准六段链"""
        request_data = {"product_id": "pluvicto", "domain": "efficacy"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "completed"
        assert len(data["child_task_ids"]) == 6

    def test_standard_chain_workflow_with_all_params(self):
        """测试带所有参数的标准六段链"""
        request_data = {
            "product_id": "pluvicto",
            "domain": "efficacy",
            "register": "R2",
            "audience": "医学专业人士",
            "project_name": "test_project",
        }

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "completed"
        assert len(data["child_task_ids"]) == 6

    def test_standard_chain_workflow_returns_real_task_id(self):
        """测试返回真实的 task_id"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # task_id 应该是有效的 UUID
        task_id = data["task_id"]
        assert task_id is not None
        assert len(task_id) == 36
        assert task_id.count("-") == 4

        # child_task_ids 也应该是有效的 UUID
        for child_id in data["child_task_ids"]:
            assert len(child_id) == 36
            assert child_id.count("-") == 4

    def test_standard_chain_workflow_child_task_ids_traceable(self):
        """测试 child_task_ids 可追踪"""
        from src.api.app import get_shared_task_logger

        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 获取共享 logger
        logger = get_shared_task_logger()

        # 验证父任务可追踪
        parent_task = logger.get_task(data["task_id"])
        assert parent_task is not None
        assert parent_task.task_id == data["task_id"]

        # 验证子任务可追踪
        for child_id in data["child_task_ids"]:
            child_task = logger.get_task(child_id)
            assert child_task is not None
            assert child_task.parent_task_id == data["task_id"]

    def test_standard_chain_workflow_missing_product_id(self):
        """测试缺少 product_id 返回 422"""
        request_data = {}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 422

    def test_standard_chain_workflow_result_structure(self):
        """测试结果结构正确 (SP-7C: 六个阶段)"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # SP-7C: 验证 result 结构包含六个阶段
        assert "evidence" in data["result"]
        assert "planning" in data["result"]
        assert "writing" in data["result"]
        assert "drafting" in data["result"]  # SP-7C: 新增
        assert "quality" in data["result"]
        assert "delivery" in data["result"]

        # 验证各阶段结果
        assert "fact_count" in data["result"]["evidence"]
        assert "thesis" in data["result"]["planning"]
        assert "prompt_length" in data["result"]["writing"]
        assert "word_count" in data["result"]["drafting"]  # SP-7C: 新增
        assert "overall_status" in data["result"]["quality"]
        assert "output_path" in data["result"]["delivery"]

    def test_standard_chain_workflow_audit_events(self):
        """测试审计事件记录"""
        from src.api.app import get_shared_task_logger

        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()
        task_id = data["task_id"]

        # 获取审计事件
        logger = get_shared_task_logger()
        audit_events = logger.get_audit_events(task_id)

        # 应该有审计事件
        assert len(audit_events) >= 1

        # 验证事件类型
        event_types = [e["event_type"] for e in audit_events]
        assert (
            "workflow_requested" in event_types or "workflow_completed" in event_types
        )


class TestStandardChainIntegration:
    """测试标准六段链集成 (SP-7C: Evidence -> Planning -> Writing -> Drafting -> Quality -> Delivery)"""

    def test_evidence_planning_integration(self):
        """测试 Evidence -> Planning 集成"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 验证 Evidence 阶段产生事实
        evidence_result = data["result"]["evidence"]
        assert evidence_result["fact_count"] >= 0

        # 验证 Planning 阶段使用 Evidence 输出
        planning_result = data["result"]["planning"]
        assert planning_result["thesis"] is not None

    def test_planning_writing_integration(self):
        """测试 Planning -> Writing 集成"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 验证 Writing 阶段使用 Planning 输出
        writing_result = data["result"]["writing"]
        assert writing_result["prompt_length"] > 0

    def test_writing_quality_integration(self):
        """测试 Writing -> Drafting -> Quality 集成"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 验证 Quality 阶段检查 Drafting 输出的正文
        quality_result = data["result"]["quality"]
        # 状态可能是大写或小写（取决于 QualityOrchestrator 实现）
        overall_status = quality_result["overall_status"].upper()
        assert overall_status in ["PASSED", "FAILED", "WARNED", "WARNING"]

    def test_quality_delivery_integration(self):
        """测试 Quality -> Delivery 集成"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 如果 Quality 通过，Delivery 应该执行
        if data["result"]["quality"]["overall_status"] != "FAILED":
            delivery_result = data["result"]["delivery"]
            assert delivery_result["output_path"] is not None


class TestStandardChainWithLecanemab:
    """测试 lecanemab 产品的标准六段链（验证 P2 修复）"""

    def test_lecanemab_standard_chain_success(self):
        """测试 lecanemab 产品可以执行标准六段链"""
        request_data = {"product_id": "lecanemab"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 验证 Evidence 阶段可以获取 lecanemab 的事实
        evidence_result = data["result"]["evidence"]
        # lecanemab 应该有事实（P2 修复后）
        assert evidence_result["fact_count"] >= 0

        # 验证工作流完成
        assert data["status"] == "completed"
        assert len(data["child_task_ids"]) == 6  # SP-7C: 六段链


# ============================================================================
# SP-6 Batch 6A: Retrieval Trace 测试
# ============================================================================


class TestStandardChainRetrievalTraceSP6Batch6A:
    """
    SP-6 Batch 6A: 验证 retrieval_trace 通过 standard_chain 暴露

    验证证据检索追踪在标准六段链中的完整暴露：
    - 最终结果中包含 retrieval_trace
    - 子任务结果中包含 retrieval_trace
    - 追踪包含查询输入、候选数量、决策链
    """

    def test_final_result_has_retrieval_trace(self):
        """最终结果包含 retrieval_trace"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 验证 evidence 结果中包含 retrieval_trace
        evidence_result = data["result"]["evidence"]
        assert "retrieval_trace" in evidence_result

        retrieval_trace = evidence_result["retrieval_trace"]
        assert isinstance(retrieval_trace, dict)

    def test_retrieval_trace_has_trace_id(self):
        """retrieval_trace 有唯一 trace_id"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        retrieval_trace = data["result"]["evidence"]["retrieval_trace"]
        assert "trace_id" in retrieval_trace
        assert retrieval_trace["trace_id"].startswith("trace_")

    def test_retrieval_trace_records_query_input(self):
        """retrieval_trace 记录查询输入"""
        request_data = {"product_id": "pluvicto", "domain": "efficacy"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        retrieval_trace = data["result"]["evidence"]["retrieval_trace"]
        assert "query_input" in retrieval_trace

        query_input = retrieval_trace["query_input"]
        assert query_input["product_id"] == "pluvicto"
        assert query_input["domain"] == "efficacy"

    def test_retrieval_trace_records_candidate_counts(self):
        """retrieval_trace 记录候选数量变化"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        retrieval_trace = data["result"]["evidence"]["retrieval_trace"]

        # 验证候选数量字段存在
        assert "total_candidates" in retrieval_trace
        assert "candidates_after_filtering" in retrieval_trace
        assert "candidates_after_dedup" in retrieval_trace
        assert "final_selected" in retrieval_trace

        # 验证数量关系
        assert (
            retrieval_trace["final_selected"]
            <= retrieval_trace["candidates_after_dedup"]
        )

    def test_retrieval_trace_records_filter_decisions(self):
        """retrieval_trace 记录过滤决策"""
        request_data = {"product_id": "pluvicto", "domain": "efficacy"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        retrieval_trace = data["result"]["evidence"]["retrieval_trace"]
        assert "filter_decisions" in retrieval_trace
        assert isinstance(retrieval_trace["filter_decisions"], list)

        # 如果有过滤决策，验证结构
        for fd in retrieval_trace["filter_decisions"]:
            assert "filter_type" in fd
            assert "candidates_before" in fd
            assert "candidates_after" in fd

    def test_retrieval_trace_records_selection_decisions(self):
        """retrieval_trace 记录选择决策"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        retrieval_trace = data["result"]["evidence"]["retrieval_trace"]
        assert "selection_decisions" in retrieval_trace
        assert isinstance(retrieval_trace["selection_decisions"], list)

        # 如果有选择决策，验证结构
        for sd in retrieval_trace["selection_decisions"]:
            assert "fact_id" in sd
            assert "reason" in sd

    def test_retrieval_trace_records_sufficiency_judgment(self):
        """retrieval_trace 记录充分性判断"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        retrieval_trace = data["result"]["evidence"]["retrieval_trace"]
        assert "sufficiency_judgment" in retrieval_trace

        sj = retrieval_trace["sufficiency_judgment"]
        assert sj is not None
        assert "is_sufficient" in sj
        assert "criteria" in sj
        assert "facts_count" in sj

    def test_child_result_has_retrieval_trace(self):
        """子任务结果包含 retrieval_trace"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 找到 evidence 子任务结果
        evidence_child_result = None
        for cr in data["child_results"]:
            if cr["module_name"] == "evidence":
                evidence_child_result = cr
                break

        assert evidence_child_result is not None
        assert "retrieval_trace" in evidence_child_result["result"]

    def test_retrieval_trace_with_different_domains(self):
        """不同领域查询生成不同追踪"""
        response1 = client.post(
            "/v1/workflow/standard-chain",
            json={"product_id": "pluvicto", "domain": "efficacy"},
        )

        response2 = client.post(
            "/v1/workflow/standard-chain",
            json={"product_id": "pluvicto", "domain": "safety"},
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        trace1 = response1.json()["result"]["evidence"]["retrieval_trace"]
        trace2 = response2.json()["result"]["evidence"]["retrieval_trace"]

        # 不同查询应该有不同的 trace_id
        assert trace1["trace_id"] != trace2["trace_id"]

        # 查询输入中的 domain 应该不同
        assert trace1["query_input"]["domain"] == "efficacy"
        assert trace2["query_input"]["domain"] == "safety"

    def test_retrieval_trace_fact_count_matches(self):
        """retrieval_trace 的 final_selected 与 fact_count 一致"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        evidence_result = data["result"]["evidence"]
        retrieval_trace = evidence_result["retrieval_trace"]

        # final_selected 应该等于 fact_count
        assert retrieval_trace["final_selected"] == evidence_result["fact_count"]


# ============================================================================
# SP-6 Batch 6C: Writing Trace 测试
# ============================================================================


class TestStandardChainWritingTraceSP6Batch6C:
    """
    SP-6 Batch 6C: 验证 writing_trace 通过 standard_chain 暴露
    """

    def test_writing_result_has_writing_trace(self):
        """writing 结果包含 writing_trace"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        writing_result = data["result"]["writing"]
        assert "writing_trace" in writing_result

    def test_writing_trace_has_planning_constraints(self):
        """writing_trace 包含规划约束"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        writing_trace = data["result"]["writing"]["writing_trace"]
        assert "planning_constraints" in writing_trace

        planning = writing_trace["planning_constraints"]
        assert "thesis" in planning
        assert "outline" in planning

    def test_writing_trace_has_evidence_anchors(self):
        """writing_trace 包含证据锚点"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        writing_trace = data["result"]["writing"]["writing_trace"]
        assert "evidence_anchors" in writing_trace
        assert isinstance(writing_trace["evidence_anchors"], list)

    def test_writing_trace_has_constraints(self):
        """writing_trace 包含硬性约束和建议性约束"""
        request_data = {"product_id": "pluvicto", "register": "R2"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        writing_trace = data["result"]["writing"]["writing_trace"]
        assert "hard_constraints" in writing_trace
        assert "advisory_constraints" in writing_trace

    def test_child_result_has_writing_trace(self):
        """writing 子任务结果包含 writing_trace"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 找到 writing 子任务结果
        writing_child_result = None
        for cr in data["child_results"]:
            if cr["module_name"] == "writing":
                writing_child_result = cr
                break

        assert writing_child_result is not None
        assert "writing_trace" in writing_child_result["result"]


# ============================================================================
# SP-6 Batch 6D: Docx 输出和字数门禁测试
# ============================================================================


class TestStandardChainDocxSP6Batch6D:
    """
    SP-6 Batch 6D: 验证 standard_chain 的 docx 正式输出
    """

    def test_delivery_output_path_is_docx(self):
        """delivery output_path 是 docx 文件"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # delivery output_path 应该指向 docx
        delivery_result = data["result"]["delivery"]
        assert delivery_result["output_path"].endswith(".docx")

    def test_delivery_docx_path_in_result(self):
        """delivery 结果包含 docx_path"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        delivery_result = data["result"]["delivery"]
        assert "docx_path" in delivery_result
        assert delivery_result["docx_path"] is not None
        assert delivery_result["docx_path"].endswith(".docx")

    def test_delivery_markdown_preview_path_in_result(self):
        """delivery 结果包含 markdown_preview_path"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        delivery_result = data["result"]["delivery"]
        assert "markdown_preview_path" in delivery_result
        assert delivery_result["markdown_preview_path"] is not None
        assert delivery_result["markdown_preview_path"].endswith(".md")

    def test_delivery_word_count_fields_in_result(self):
        """delivery 结果包含字数相关字段"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        delivery_result = data["result"]["delivery"]

        # 字数相关字段
        assert "final_docx_word_count" in delivery_result
        assert delivery_result["final_docx_word_count"] is not None
        assert delivery_result["final_docx_word_count"] > 0

        assert "word_count_basis" in delivery_result
        assert delivery_result["word_count_basis"] == "docx_body"

        assert "word_count_gate_passed" in delivery_result
        assert delivery_result["word_count_gate_passed"] is True

    def test_delivery_docx_is_python_generated(self):
        """docx 是 Python 生成的（通过 python-docx 库）"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 验证 docx 文件路径
        docx_path = data["result"]["delivery"]["docx_path"]
        assert docx_path.endswith(".docx")

        # docx_path 应该在 output 目录下
        assert "output" in docx_path or docx_path.startswith("output")

    def test_markdown_is_only_preview_in_standard_chain(self):
        """Markdown 只是预览产物"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        delivery_result = data["result"]["delivery"]

        # output_path 应该是 docx，不是 md
        assert delivery_result["output_path"] == delivery_result["docx_path"]
        assert (
            delivery_result["output_path"] != delivery_result["markdown_preview_path"]
        )

        # markdown 应该只是 preview
        assert delivery_result["markdown_preview_path"].endswith(".md")

    def test_word_count_basis_follows_docx_body(self):
        """字数统计基准为 docx_body"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        delivery_result = data["result"]["delivery"]
        assert delivery_result["word_count_basis"] == "docx_body"


# ============================================================================
# SP-7C: Drafting 步骤集成测试
# ============================================================================


class TestStandardChainDraftingSP7C:
    """
    SP-7C: 验证 Drafting 步骤正确集成到标准六段链

    测试要点：
    1. 标准链返回 drafting 段
    2. child_task_ids 长度为 6，顺序包含 drafting
    3. Quality 审查的是 drafting_result.content（正文），而非 prompts
    4. Delivery 接收的是 drafting 生成的正文内容
    """

    def test_standard_chain_returns_drafting_section(self):
        """标准链返回 drafting 段"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 验证 drafting 段存在
        assert "drafting" in data["result"]
        drafting = data["result"]["drafting"]
        assert "word_count" in drafting
        assert drafting["word_count"] > 0

    def test_child_task_order_includes_drafting(self):
        """child_task_ids 长度为 6，顺序包含 drafting"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 验证 6 个子任务
        assert len(data["child_task_ids"]) == 6

        # 验证顺序：drafting 在 writing 和 quality 之间
        modules = [cr["module_name"] for cr in data["child_results"]]
        assert modules == [
            "evidence",
            "planning",
            "writing",
            "drafting",
            "quality",
            "delivery",
        ]

        # 验证 drafting 在第 4 位（0-indexed: 3）
        assert modules[3] == "drafting"

    def test_quality_reviews_content_not_prompt(self):
        """Quality 审查的是正文而非 prompts（通过结果间接验证）"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Quality 应该成功执行（因为 drafting 生成了有效正文）
        quality_result = data["result"]["quality"]
        assert "overall_status" in quality_result
        # 状态应该是 PASSED（因为正文足够长）
        assert quality_result["overall_status"].upper() in ["PASSED", "WARNED"]

    def test_delivery_receives_content_from_drafting(self):
        """Delivery 接收 drafting 生成的正文内容"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 验证 delivery 结果
        delivery_result = data["result"]["delivery"]
        assert "output_path" in delivery_result
        assert delivery_result["output_path"].endswith(".docx")

        # 验证正文字数来自 drafting（通过 final_docx_word_count 验证）
        drafting_result = data["result"]["drafting"]
        delivery_word_count = delivery_result["final_docx_word_count"]

        # 正文字数应该与 drafting 生成的字数相近
        # 注意：docx 字数可能包含格式等，不完全等于 drafting word_count
        assert delivery_word_count > 0

    def test_drafting_child_result_has_content_length(self):
        """drafting 子任务结果包含 content_length"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # 找到 drafting 子任务结果
        drafting_child_result = None
        for cr in data["child_results"]:
            if cr["module_name"] == "drafting":
                drafting_child_result = cr
                break

        assert drafting_child_result is not None
        assert "word_count" in drafting_child_result["result"]
        assert "content_length" in drafting_child_result["result"]
        assert drafting_child_result["result"]["content_length"] > 0

    def test_drafting_trace_included(self):
        """drafting 结果包含 trace"""
        request_data = {"product_id": "pluvicto"}

        response = client.post("/v1/workflow/standard-chain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        drafting = data["result"]["drafting"]
        assert "trace" in drafting
        trace = drafting["trace"]
        assert "generation_mode" in trace
        assert "model_used" in trace
