"""旅行计划 API 路由."""

import logging
from fastapi import APIRouter, Query, HTTPException

from app.models.travel_plan import TravelPlanCreateRequest, TravelPlanResponse
from app.services.city_service import city_service
from app.services.travel_plan_service import (
    generate_travel_plan,
    validate_request,
    TravelPlanValidationError,
)

logger = logging.getLogger("travel-helper")

router = APIRouter(tags=["旅行计划"])


@router.post(
    "/travel-plans/generate",
    response_model=TravelPlanResponse,
    summary="生成旅行计划",
)
async def create_travel_plan(request: TravelPlanCreateRequest):
    """基于用户输入生成个性化旅行计划.

    - 校验目的地、日期、偏好
    - 调用 LLM 生成旅行计划
    - 返回结构化的行程结果
    """
    try:
        validate_request(request)
    except TravelPlanValidationError as e:
        raise HTTPException(status_code=404, detail=[{"field": "destination", "message": str(e)}])

    try:
        return await generate_travel_plan(request)
    except RuntimeError as e:
        logger.error(f"旅行计划生成失败: {e}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/cities/search", summary="城市搜索")
async def search_cities(q: str = Query(..., min_length=1, description="搜索关键字")):
    """城市搜索与自动补全.

    支持按城市名称和拼音搜索，返回匹配的城市列表。
    """
    results = city_service.search(q)
    return {
        "cities": [
            {
                "name": c.name,
                "pinyin": c.pinyin,
                "province": c.province,
                "code": c.code,
            }
            for c in results
        ]
    }
