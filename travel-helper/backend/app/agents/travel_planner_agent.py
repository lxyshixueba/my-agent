"""旅行规划智能体 — LangChain ChatPromptTemplate 版本.

使用 LangChain ChatPromptTemplate 构建 prompt，
绑定 Pydantic 输出模型，替代原始的硬编码 prompt 构建方式。
"""

import logging
from typing import Any

from app.models.travel_plan import TravelPlanCreateRequest
from app.templates.travel_planner.create import (
    CREATE_SYSTEM_PROMPT,
    build_create_user_prompt,
)

logger = logging.getLogger("travel-helper")


# =============================================================================
# Prompt 模板
# =============================================================================

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# 创建旅行计划的 ChatPromptTemplate
CREATE_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(CREATE_SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(
        "请为我规划一份{days}天的{destination}旅行计划。\n"
        "出发日期: {start_date}\n"
        "结束日期: {end_date}\n"
        "交通方式: {transport}\n"
        "住宿偏好: {accommodation}\n"
        "{preferences_text}\n"
        "{special_requests_text}"
    ),
])


def _build_prompt_vars(request: TravelPlanCreateRequest) -> dict[str, Any]:
    """将 TravelPlanCreateRequest 转换为 prompt 模板变量."""
    transport_map = {
        "flight": "飞机",
        "high_speed_rail": "高铁",
        "self_driving": "自驾",
        "bus": "大巴",
    }
    accommodation_map = {
        "economy": "经济型酒店",
        "comfort": "舒适型酒店",
        "premium": "高档型酒店",
        "luxury": "豪华酒店",
        "homestay": "民宿",
    }
    preference_map = {
        "sightseeing": "景点观光",
        "food": "美食",
        "nature": "自然风光",
        "history_culture": "历史文化",
        "shopping": "购物体验",
        "adventure": "探险",
        "cultural_experience": "文化体验",
        "leisure_entertainment": "休闲娱乐",
    }

    preferences_text = ""
    if request.preferences:
        pref_names = [preference_map.get(p.value if hasattr(p, 'value') else p, p) for p in request.preferences]
        preferences_text = f"旅行偏好: {'、'.join(pref_names)}"

    special_requests_text = ""
    if request.special_requirements:
        special_requests_text = f"特殊要求: {request.special_requirements}"

    return {
        "days": request.days,
        "destination": request.destination.name,
        "start_date": str(request.start_date),
        "end_date": str(request.end_date),
        "transport": transport_map.get(request.transport_mode.value if hasattr(request.transport_mode, 'value') else request.transport_mode, request.transport_mode),
        "accommodation": accommodation_map.get(request.accommodation.value if hasattr(request.accommodation, 'value') else request.accommodation, request.accommodation),
        "preferences_text": preferences_text,
        "special_requests_text": special_requests_text,
    }


def build_prompts(request: TravelPlanCreateRequest) -> tuple[str, str]:
    """构建完整的系统提示词和用户提示词.

    兼容旧的调用方式，内部使用 ChatPromptTemplate 构建。

    Args:
        request: 旅行计划创建请求

    Returns:
        (system_prompt, user_prompt) 元组
    """
    vars_dict = _build_prompt_vars(request)
    user_prompt = build_create_user_prompt(
        destination=vars_dict["destination"],
        days=vars_dict["days"],
        start_date=vars_dict["start_date"],
        end_date=vars_dict["end_date"],
        transport=vars_dict["transport"],
        accommodation=vars_dict["accommodation"],
        preferences=request.preferences,
        special_requests=request.special_requirements,
    )
    return CREATE_SYSTEM_PROMPT, user_prompt


async def generate_travel_plan_with_structured_output(
    request: TravelPlanCreateRequest,
    output_model: type,
) -> Any:
    """使用结构化输出生成旅行计划.

    Args:
        request: 旅行计划创建请求
        output_model: Pydantic 输出模型（如 TravelPlanOutput）

    Returns:
        解析后的 Pydantic 模型实例
    """
    from app.services.llm_service import llm_service

    vars_dict = _build_prompt_vars(request)
    user_prompt = CREATE_PROMPT_TEMPLATE.format(**vars_dict)

    result = await llm_service.generate_structured(
        system_prompt=CREATE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        output_model=output_model,
    )
    return result
