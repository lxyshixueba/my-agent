"""编辑每日行程提示词模板.

用于 AI 辅助编辑场景：当用户通过前端拖拽/删除景点后，
可调用此模板重新生成该天的行程时间线和相关内容。
"""

from app.templates._common import (
    ROLE_DEFINITION,
    OUTPUT_FORMAT_CONSTRAINTS,
    PLANNING_PRINCIPLES,
)

EDIT_DAY_SYSTEM_PROMPT = f"""{ROLE_DEFINITION}

用户正在编辑某一日天的行程，已经通过前端进行了景点顺序调整或删除操作。
你的任务是重新生成该天的行程时间线（schedule），确保与更新后的景点列表匹配。

{PLANNING_PRINCIPLES}

{OUTPUT_FORMAT_CONSTRAINTS}

**编辑场景特殊要求**：
1. 根据用户调整后的景点顺序，合理安排每个景点的游玩时间段
2. 保留原有的住宿、餐饮、交通安排（除非用户明确要求修改）
3. 景点之间的交通时间要合理
4. 总游玩时间不要超过当日可用时间范围
"""


def build_edit_day_user_prompt(
    day_index: int,
    date: str,
    attractions: list[dict],
    accommodation: dict | None = None,
    dining: dict | None = None,
    transportation: list[dict] | None = None,
    original_schedule: list[dict] | None = None,
) -> str:
    """构建编辑行程用户提示词.

    Args:
        day_index: 第几天（从 1 开始）
        date: 具体日期（YYYY-MM-DD）
        attractions: 更新后的景点列表（每个包含 name, play_duration 等）
        accommodation: 住宿安排
        dining: 餐饮安排
        transportation: 交通安排
        original_schedule: 原始时间线（可选，用于参考）

    Returns:
        格式化的用户提示词
    """
    parts = [
        f"请为第 {day_index} 天（{date}）重新生成行程时间线。",
        f"更新后的景点列表（共 {len(attractions)} 个）：",
    ]

    for i, attr in enumerate(attractions, 1):
        parts.append(
            f"  {i}. {attr.get('name', '未知景点')}（游玩时长: {attr.get('play_duration', '未指定')}）"
        )
        if attr.get('description'):
            parts.append(f"     描述: {attr['description']}")

    if original_schedule:
        parts.append("\n原始时间线参考：")
        for slot in original_schedule:
            parts.append(
                f"  {slot.get('start_time', slot.get('startTime', '?'))} - "
                f"{slot.get('end_time', slot.get('endTime', '?'))}: "
                f"{slot.get('activity', '')}"
            )

    if accommodation:
        parts.append(f"\n住宿: {accommodation.get('hotel_name', accommodation.get('hotelName', '未指定'))}")

    if dining:
        parts.append(f"\n餐饮: 早餐-{dining.get('breakfast', '未指定')}, 午餐-{dining.get('lunch', '未指定')}, 晚餐-{dining.get('dinner', '未指定')}")

    if transportation:
        parts.append("\n交通安排：")
        for t in transportation:
            parts.append(f"  - {t.get('type', '未知')}: {t.get('description', '')}")

    parts.append("\n请根据以上信息重新生成合理的时间线安排。")

    return "\n".join(parts)


EDIT_DAY_PROMPT = {
    "system": EDIT_DAY_SYSTEM_PROMPT,
    "user_builder": build_edit_day_user_prompt,
}
