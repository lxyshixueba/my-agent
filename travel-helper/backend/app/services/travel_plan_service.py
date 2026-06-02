"""旅行计划生成服务."""

import json
import logging
import uuid
from datetime import datetime, timezone, timedelta

from app.agents.travel_planner_agent import build_prompts
from app.config import settings
from app.models.travel_plan import (
    TravelPlanCreateRequest,
    TravelPlanResponse,
)
from app.services.city_service import CityService
from app.services.llm_service import LLMService

logger = logging.getLogger("travel-helper")

# 实例化依赖
city_service = CityService()
llm_service = LLMService()


class TravelPlanValidationError(Exception):
    """旅行计划请求校验错误."""

    pass


def validate_request(request: TravelPlanCreateRequest) -> None:
    """校验旅行计划请求.

    Args:
        request: 旅行计划创建请求

    Raises:
        TravelPlanValidationError: 校验失败时抛出
    """
    # 验证城市存在性
    if not city_service.exists(request.destination.name, request.destination.code):
        raise TravelPlanValidationError(f"未找到匹配的城市: {request.destination.name}")

    # 验证天数上限
    if request.days > 30:
        raise TravelPlanValidationError("出行天数不能超过 30 天")


async def generate_travel_plan(request: TravelPlanCreateRequest) -> TravelPlanResponse:
    """生成旅行计划.

    Args:
        request: 旅行计划创建请求

    Returns:
        生成的旅行计划响应

    Raises:
        TravelPlanValidationError: 请求校验失败
        RuntimeError: LLM 调用失败
    """
    # 校验请求
    validate_request(request)

    request_id = str(uuid.uuid4())[:8]
    logger.info(f"开始生成旅行计划 [req:{request_id}]")

    # 构建 prompt
    system_prompt, user_prompt = build_prompts(request)

    # 调用 LLM
    try:
        raw_response = await llm_service.generate(system_prompt, user_prompt)
    except Exception as e:
        logger.error(f"LLM 调用失败 [req:{request_id}]: {e}")
        raise RuntimeError("旅行计划生成失败，请稍后重试") from e

    # 解析 LLM 响应
    try:
        # 移除可能的 markdown 代码块标记
        content = raw_response.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        plan_data = json.loads(content)

        # 设置时区
        tz = timezone(timedelta(hours=8))
        generated_at = datetime.now(tz).isoformat()

        response = TravelPlanResponse(
            request_id=request_id,
            destination=request.destination.name,
            days=request.days,
            daily_itineraries=plan_data.get("daily_itineraries", []),
            generated_at=generated_at,
        )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error(f"LLM 响应解析失败 [req:{request_id}]: {e}")
        raise RuntimeError("旅行计划生成失败，返回格式异常") from e

    logger.info(f"旅行计划生成成功 [req:{request_id}]")
    return response
