"""
Evidence API Routes

证据查询 API 端点。
包含证据查询、溯源和统计聚合接口。
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.modules.evidence.service import EvidenceService
from src.modules.evidence.models import FactRecord, SourceRecord
from src.assembly import get_evidence_service


router = APIRouter(prefix="/v1/evidence", tags=["evidence"])


# ==================== Request/Response Models ====================

class EvidenceQueryRequest(BaseModel):
    """证据查询请求"""
    product_id: str = Field(..., description="产品 ID")
    domain: Optional[str] = Field(None, description="领域过滤 (efficacy, safety, biomarker, moa)")
    fact_keys: Optional[List[str]] = Field(None, description="事实键列表")
    limit: int = Field(default=100, description="返回数量限制")


class FactRecordResponse(BaseModel):
    """事实记录响应"""
    fact_id: str
    product_id: str
    domain: str
    fact_key: str
    value: str
    definition: Optional[str] = None
    definition_zh: Optional[str] = None
    unit: Optional[str] = None
    status: str
    lineage: dict = Field(default_factory=dict)


class SourceRecordResponse(BaseModel):
    """来源记录响应"""
    source_id: str
    source_type: str
    title: str
    product_id: Optional[str] = None
    source_keys: List[str] = Field(default_factory=list)


class FactLineageResponse(BaseModel):
    """事实溯源响应"""
    fact_id: str
    product_id: Optional[str] = None
    lineage: dict = Field(default_factory=dict)
    sources: List[str] = Field(default_factory=list)


class ProductListResponse(BaseModel):
    """产品列表响应"""
    products: List[str]
    count: int


# ==================== Endpoints ====================

@router.post("/query", response_model=List[FactRecordResponse])
async def query_evidence(request: EvidenceQueryRequest):
    """
    查询证据
    
    根据产品 ID 和可选的领域/事实键过滤条件查询证据。
    
    Args:
        request: 查询请求
        
    Returns:
        匹配的 FactRecord 列表
    """
    service = get_evidence_service()
    
    facts = service.resolve_facts({
        "product_id": request.product_id,
        "domain": request.domain,
        "fact_keys": request.fact_keys or [],
        "limit": request.limit
    })
    
    return [
        FactRecordResponse(
            fact_id=f.fact_id,
            product_id=f.product_id,
            domain=f.domain,
            fact_key=f.fact_key,
            value=str(f.value) if f.value is not None else "",
            definition=f.definition,
            definition_zh=f.definition_zh,
            unit=f.unit,
            status=f.status.value,
            lineage=f.lineage
        )
        for f in facts
    ]


@router.get("/fact/{fact_id}", response_model=FactLineageResponse)
async def get_fact_detail(fact_id: str):
    """
    获取单条事实详情及溯源
    
    Args:
        fact_id: 事实 ID
        
    Returns:
        事实详情及溯源信息
    """
    service = get_evidence_service()
    
    lineage = service.get_fact_lineage(fact_id)
    
    return FactLineageResponse(
        fact_id=lineage.get("fact_id", fact_id),
        product_id=lineage.get("product_id"),
        lineage=lineage.get("lineage", {}),
        sources=lineage.get("sources", [])
    )


@router.get("/products", response_model=ProductListResponse)
async def list_products():
    """
    列出所有可用的产品 ID
    
    Returns:
        产品 ID 列表
    """
    service = get_evidence_service()
    
    products = service.list_available_products()
    
    return ProductListResponse(
        products=products,
        count=len(products)
    )


@router.get("/sources/{product_id}", response_model=List[SourceRecordResponse])
async def get_sources(
    product_id: str,
    source_type: Optional[str] = Query(None, description="来源类型过滤")
):
    """
    获取产品的来源列表
    
    Args:
        product_id: 产品 ID
        source_type: 可选的来源类型过滤
        
    Returns:
        SourceRecord 列表
    """
    service = get_evidence_service()
    
    sources = service.resolve_sources({
        "product_id": product_id,
        "source_type": source_type
    })
    
    return [
        SourceRecordResponse(
            source_id=s.source_id,
            source_type=s.source_type.value,
            title=s.title,
            product_id=s.product_id,
            source_keys=s.source_keys
        )
        for s in sources
    ]


# ==================== 证据统计聚合接口 ====================


class SourceTypeCount(BaseModel):
    """来源类型计数"""
    source_type: str
    count: int


class EvidenceStatsResponse(BaseModel):
    """
    证据统计聚合响应

    基于 consumer 目录当前数据的实时统计。
    """
    total_facts: int = Field(description="事实总数")
    total_sources: int = Field(description="来源总数")
    total_products: int = Field(description="产品总数")
    source_type_distribution: dict[str, int] = Field(
        default_factory=dict, description="来源类型分布 {type: count}"
    )
    products: List[str] = Field(default_factory=list, description="可用产品列表")
    freshness: str = Field(description="统计时间 (ISO 8601)")


@router.get("/stats", response_model=EvidenceStatsResponse)
async def get_evidence_stats():
    """
    获取证据统计聚合数据

    返回当前 consumer 目录下的证据总量、类型分布和产品覆盖信息。
    基于真实数据，不是 mock 或手写配置。
    """
    service = get_evidence_service()

    products = service.list_available_products()

    # 聚合各产品的来源信息
    type_counter: dict[str, int] = {}
    total_facts = 0
    total_sources = 0

    for product_id in products:
        try:
            # 获取来源
            sources = service.resolve_sources({"product_id": product_id})
            total_sources += len(sources)
            for s in sources:
                st = s.source_type.value
                type_counter[st] = type_counter.get(st, 0) + 1

            # 获取事实
            facts = service.resolve_facts({
                "product_id": product_id,
                "fact_keys": [],
                "limit": 10000,
            })
            total_facts += len(facts)
        except Exception:
            continue

    return EvidenceStatsResponse(
        total_facts=total_facts,
        total_sources=total_sources,
        total_products=len(products),
        source_type_distribution=dict(sorted(type_counter.items())),
        products=products,
        freshness=datetime.now().isoformat(),
    )