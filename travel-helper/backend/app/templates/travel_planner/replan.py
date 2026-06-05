"""重新规划行程提示词模板."""

from app.templates._common import (
    ROLE_DEFINITION,
    OUTPUT_FORMAT_CONSTRAINTS,
    PLANNING_PRINCIPLES,
)

REPLAN_SYSTEM_PROMPT = f"""{ROLE_DEFINITION}

你当前正在为用户重新规划一段已有的旅行行程。用户可能对原有行程不满意，或对某些部分做了手动调整，现在需要你在保留用户合理修改的基础上，重新生成一份完整、连贯的行程方案。

{PLANNING_PRINCIPLES}

{OUTPUT_FORMAT_CONSTRAINTS}

**特别注意**：
1. 如果用户提供了编辑痕迹（如删除了某景点、调整了顺序），请尊重这些修改，不要恢复被用户删除的内容
2. 重新规划后的行程必须覆盖全部天数，每日安排连贯
3. 预算、住宿、餐饮、交通等配套信息需要同步更新
4. 返回严格的 JSON，与原始行程格式一致"""


def build_replan_user_prompt(
    destination: str,
    days: int,
    start_date: str,
    end_date: str,
    transport: str,
    accommodation: str,
    preferences: list[str] | None = None,
    special_requests: str | None = None,
    current_itinerary: str | None = None,
    edit_traces: str | None = None,
    new_constraints: str | None = None,
) -> str:
    """构建重新规划用户提示词.

    Args:
        destination: 目的地城市
        days: 出行天数
        start_date: 出发日期
        end_date: 返回日期
        transport: 交通方式（中文）
        accommodation: 住宿偏好（中文）
        preferences: 偏好标签列表（中文）
        special_requests: 特殊要求
        current_itinerary: 当前行程 JSON 字符串（供 LLM 参考）
        edit_traces: 用户编辑痕迹描述（如"删除了第2天的故宫""调整了第3天景点顺序"）
        new_constraints: 新增约束条件（如"增加一天去长城""希望每天不超过2个景点"）

    Returns:
        格式化的重新规划用户提示词
    """
    parts = [
        f"请为我重新规划一份{days}天的{destination}旅行计划。",
        f"出发日期: {start_date}",
        f"结束日期: {end_date}",
        f"交通方式: {transport}",
        f"住宿偏好: {accommodation}",
    ]

    if preferences:
        parts.append(f"旅行偏好: {'、'.join(preferences)}")

    if special_requests:
        parts.append(f"特殊要求: {special_requests}")

    # 注入当前行程供参考
    if current_itinerary:
        parts.append(f"\n**当前行程安排**（请在此基础上调整）：\n{current_itinerary}")

    # 注入用户编辑痕迹
    if edit_traces:
        parts.append(f"\n**用户已做的修改**（请尊重这些变更）：\n{edit_traces}")

    # 注入新约束
    if new_constraints:
        parts.append(f"\n**新增约束条件**：\n{new_constraints}")

    parts.append("\n请根据以上信息，重新生成完整的行程方案。")

    return "\n".join(parts)
