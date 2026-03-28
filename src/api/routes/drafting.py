"""
Drafting API Routes

独立成稿 API 端点。

SP-7B: 新增 /v1/drafting/generate 端点。
SP-7B FIX1: 严格请求契约 + openai 路径显式接线。
"""

import os

from fastapi import APIRouter, Depends, HTTPException

from src.adapters.llm_gateway import LLMGateway, create_llm_provider_from_env
from src.api.app import get_shared_task_logger
from src.contracts.base import ModuleName
from src.modules.drafting.models import DraftingInput, DraftingRequest, DraftingResponse
from src.modules.drafting.service import DraftingService
from src.runtime_logging import TaskLogger


router = APIRouter(prefix="/v1/drafting", tags=["drafting"])


async def get_drafting_service() -> DraftingService:
    """
    获取 DraftingService 实例。

    fake 模式沿用现有确定性本地成稿；openai 模式必须显式注入 gateway。
    """
    provider_name = os.environ.get("LLM_PROVIDER", "fake").lower()

    if provider_name == "openai":
        provider, gateway_config = create_llm_provider_from_env()
        gateway = LLMGateway(provider, gateway_config)
        return DraftingService(llm_gateway=gateway, default_mode="openai")

    if provider_name == "fake":
        return DraftingService()

    raise ValueError(
        f"Unknown LLM_PROVIDER: '{provider_name}'. "
        "Supported values: 'fake', 'openai'."
    )


async def get_task_logger():
    """获取应用级共享的 TaskLogger 实例。"""
    return get_shared_task_logger()


@router.post("/generate", response_model=DraftingResponse)
async def generate_content(
    request: DraftingRequest,
    service: DraftingService = Depends(get_drafting_service),
    logger: TaskLogger = Depends(get_task_logger),
):
    """
    生成正文内容。
    """
    task_id = logger.start_task(
        module=ModuleName.DRAFTING,
        input_data={
            "system_prompt_length": len(request.system_prompt),
            "user_prompt_length": len(request.user_prompt),
            "target_word_count": request.target_word_count,
        },
        metadata={"model_config": request.model_config_data},
    )

    try:
        drafting_input = DraftingInput(
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt,
            model_config=request.model_config_data,
            target_word_count=request.target_word_count,
            metadata=request.metadata,
        )
        result = service.generate(drafting_input)

        logger.complete_task(
            task_id=task_id,
            output_data={
                "word_count": result.word_count,
                "content_length": len(result.content),
                "generation_mode": result.trace.generation_mode,
            },
        )

        return DraftingResponse(
            task_id=task_id,
            content=result.content,
            word_count=result.word_count,
            trace=result.trace.to_dict(),
            metadata=result.metadata,
        )

    except Exception as exc:
        logger.fail_task(task_id=task_id, error_message=str(exc))
        raise HTTPException(status_code=500, detail=f"成稿失败: {exc}") from exc


@router.get("/health")
async def health_check():
    """健康检查。"""
    return {"status": "ok", "module": "drafting"}
