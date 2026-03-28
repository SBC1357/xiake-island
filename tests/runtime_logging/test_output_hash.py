"""
SP-4 output_hash auto-compute test
验证 complete_task(output_data=...) 自动计算 output_hash
"""
import pytest


def test_complete_task_auto_computes_output_hash():
    """测试 complete_task 自动计算 output_hash"""
    from src.runtime_logging import TaskLogger, MemoryTaskLogStore, compute_output_hash
    from src.contracts.base import ModuleName
    
    logger = TaskLogger(MemoryTaskLogStore())
    
    # 启动任务
    task_id = logger.start_task(
        module=ModuleName.OPINION,
        input_data={"audience": "医生", "content": "test"}
    )
    
    # 完成任务，只提供 output_data，不提供 output_hash
    output_data = {"content": "生成的内容", "status": "completed"}
    logger.complete_task(task_id, output_data=output_data, duration_ms=100)
    
    # 验证 output_hash 被自动计算
    entry = logger.get_task(task_id)
    assert entry is not None
    assert entry.output_hash is not None
    assert entry.output_hash == compute_output_hash(output_data)


def test_complete_task_preserves_explicit_output_hash():
    """测试 complete_task 保留显式传入的 output_hash"""
    from src.runtime_logging import TaskLogger, MemoryTaskLogStore
    from src.contracts.base import ModuleName
    
    logger = TaskLogger(MemoryTaskLogStore())
    
    task_id = logger.start_task(
        module=ModuleName.OPINION,
        input_data={"audience": "医生"}
    )
    
    # 完成任务，显式提供 output_hash
    explicit_hash = "explicit_hash_123"
    logger.complete_task(
        task_id, 
        output_data={"content": "test"},
        output_hash=explicit_hash
    )
    
    entry = logger.get_task(task_id)
    assert entry is not None
    assert entry.output_hash == explicit_hash


def test_compute_output_hash_export():
    """测试 compute_output_hash 从 runtime_logging 导出"""
    from src.runtime_logging import compute_output_hash
    
    result = compute_output_hash({"content": "test"})
    assert isinstance(result, str)
    assert len(result) == 16