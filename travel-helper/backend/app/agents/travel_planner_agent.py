"""旅行规划智能体 — 构建 LLM prompt."""

import json
from app.models.travel_plan import TravelPlanCreateRequest, PreferenceTag

# 交通方式中文映射
TRANSPORT_MAP = {
    "flight": "飞机",
    "high_speed_rail": "高铁",
    "self_driving": "自驾",
    "bus": "大巴",
}

# 住宿偏好中文映射
ACCOMMODATION_MAP = {
    "economy": "经济型酒店",
    "comfort": "舒适型酒店",
    "premium": "高档型酒店",
    "luxury": "豪华酒店",
    "homestay": "民宿",
}

# 旅行偏好中文映射
PREFERENCE_MAP = {
    "sightseeing": "景点观光",
    "food": "美食",
    "nature": "自然风光",
    "history_culture": "历史文化",
    "shopping": "购物体验",
    "adventure": "探险",
    "cultural_experience": "文化体验",
    "leisure_entertainment": "休闲娱乐",
}


SYSTEM_PROMPT = """你是一位资深的旅行规划师。你的任务是根据用户提供的旅行信息，生成一份详细的个性化旅行计划。

请遵循以下原则：
1. 每天的行程安排要合理，不要过于紧凑
2. 推荐的景点、餐厅要具有当地特色
3. 考虑用户的偏好标签，优先推荐相关类型的活动
4. 如果有特殊服务要求，请在行程中体现
5. 返回格式必须是严格的 JSON，符合以下 schema：

{
  "destination": "城市名称",
  "days": 出行天数,
  "daily_itineraries": [
    {
      "day": 1,
      "date": "YYYY-MM-DD",
      "theme": "当日主题",
      "activities": [
        {
          "type": "attraction|restaurant|shopping|activity",
          "name": "名称",
          "description": "详细描述",
          "time_slot": "morning|afternoon|evening",
          "duration_minutes": 预计时长（分钟）
        }
      ]
    }
  ]
}

只返回 JSON，不要包含其他文字。"""


def build_user_prompt(request: TravelPlanCreateRequest) -> str:
    """构建用户提示词.

    Args:
        request: 旅行计划创建请求

    Returns:
        格式化的用户提示词
    """
    parts = [
        f"请为我规划一份{request.days}天的{request.destination.name}旅行计划。",
        f"出发日期: {request.start_date}",
        f"结束日期: {request.end_date}",
        f"交通方式: {TRANSPORT_MAP.get(request.transport_mode, request.transport_mode)}",
        f"住宿偏好: {ACCOMMODATION_MAP.get(request.accommodation, request.accommodation)}",
    ]

    if request.preferences:
        pref_names = [PREFERENCE_MAP.get(p, p) for p in request.preferences]
        parts.append(f"旅行偏好: {'、'.join(pref_names)}")

    if request.special_requirements:
        parts.append(f"特殊要求: {request.special_requirements}")

    return "\n".join(parts)


def build_prompts(request: TravelPlanCreateRequest) -> tuple[str, str]:
    """构建完整的系统提示词和用户提示词.

    Args:
        request: 旅行计划创建请求

    Returns:
        (system_prompt, user_prompt) 元组
    """
    return SYSTEM_PROMPT, build_user_prompt(request)
