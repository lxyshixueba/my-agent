"""旅行计划创建提示词."""

from app.templates._common import (
    ROLE_DEFINITION,
    OUTPUT_FORMAT_CONSTRAINTS,
    PLANNING_PRINCIPLES,
)

CREATE_SYSTEM_PROMPT = f"""{ROLE_DEFINITION}

{PLANNING_PRINCIPLES}

{OUTPUT_FORMAT_CONSTRAINTS}"""


def build_create_user_prompt(
    destination: str,
    days: int,
    start_date: str,
    end_date: str,
    transport: str,
    accommodation: str,
    preferences: list[str] | None = None,
    special_requests: str | None = None,
) -> str:
    """构建旅行计划创建用户提示词.

    Args:
        destination: 目的地城市
        days: 出行天数
        start_date: 出发日期
        end_date: 返回日期
        transport: 交通方式（中文）
        accommodation: 住宿偏好（中文）
        preferences: 偏好标签列表（中文）
        special_requests: 特殊要求

    Returns:
        格式化的用户提示词
    """
    parts = [
        f"请为我规划一份{days}天的{destination}旅行计划。",
        f"出发日期: {start_date}",
        f"结束日期: {end_date}",
        f"交通方式: {transport}",
        f"住宿偏好: {accommodation}",
    ]

    if preferences:
        parts.append(f"旅行偏好: {'、'.join(preferences)}")

    if special_requests:
        parts.append(f"特殊要求: {special_requests}")

    return "\n".join(parts)


CREATE_USER_PROMPT_TEMPLATE = build_create_user_prompt
