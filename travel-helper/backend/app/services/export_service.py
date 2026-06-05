"""旅行计划导出服务 — 生成文本/HTML 格式的导出内容."""

from app.models.travel_plan import TravelPlanFull


def generate_text_export(plan: TravelPlanFull) -> str:
    """生成纯文本格式的旅行计划.

    Args:
        plan: 完整的旅行计划数据

    Returns:
        纯文本字符串
    """
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append(f"  旅行计划 — {plan.destination.name}")
    lines.append("=" * 60)
    lines.append("")

    # 基本信息
    lines.append(f"目的地: {plan.destination.name}")
    if plan.description:
        lines.append(f"简介: {plan.description}")
    lines.append(f"日期: {plan.date_range.start_date} ~ {plan.date_range.end_date}")
    lines.append("")

    # 偏好
    if plan.preferences:
        lines.append("--- 旅行偏好 ---")
        lines.append(f"住宿: {plan.preferences.accommodation_type}")
        lines.append(f"交通: {plan.preferences.transportation}")
        if plan.preferences.tags:
            lines.append(f"标签: {', '.join(plan.preferences.tags)}")
        if plan.preferences.special_requests:
            lines.append(f"特殊要求: {plan.preferences.special_requests}")
        lines.append("")

    # 预算
    lines.append("--- 预算明细 (CNY) ---")
    lines.append(f"景点门票: {plan.budget.attraction_tickets:.2f}")
    lines.append(f"酒店住宿: {plan.budget.hotel_accommodation:.2f}")
    lines.append(f"餐饮交通: {plan.budget.dining_transport:.2f}")
    lines.append(f"餐饮美食: {plan.budget.dining_food:.2f}")
    lines.append(f"总计: {plan.budget.total:.2f}")
    lines.append("")

    # 每日行程
    lines.append("--- 每日行程 ---")
    for day in plan.daily_itineraries:
        lines.append(f"\n第 {day.day_index} 天 ({day.date})")
        lines.append(f"  概要: {day.summary}")

        # 天气
        if day.weather:
            temp = day.weather.temperature
            temp_str = f"{temp.low}~{temp.high}" if temp else "未知"
            lines.append(f"  天气: {day.weather.condition} {temp_str}度")

        # 日程
        if day.schedule:
            lines.append("  日程:")
            for slot in day.schedule:
                lines.append(f"    {slot.start_time}-{slot.end_time} {slot.activity}")

        # 景点
        if day.attractions:
            lines.append("  景点:")
            for attr in day.attractions:
                lines.append(f"    - {attr.name} ({attr.play_duration})")

        # 住宿
        if day.accommodation:
            lines.append(f"  住宿: {day.accommodation.hotel_name} ({day.accommodation.room_type})")

        # 餐饮
        if day.dining:
            lines.append(f"  餐饮: 早餐={day.dining.breakfast} | 午餐={day.dining.lunch} | 晚餐={day.dining.dinner}")

        # 交通
        if day.transportation:
            lines.append("  交通:")
            for t in day.transportation:
                lines.append(f"    {t.type}: {t.description}")

    lines.append("")
    lines.append(f"创建时间: {plan.created_at}")
    lines.append(f"更新时间: {plan.updated_at}")
    lines.append("=" * 60)

    return "\n".join(lines)


def generate_html_export(plan: TravelPlanFull) -> str:
    """生成 HTML 格式的旅行计划（适合浏览器打印为 PDF）.

    Args:
        plan: 完整的旅行计划数据

    Returns:
        HTML 字符串
    """
    html_parts: list[str] = []

    html_parts.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
body { font-family: "Microsoft YaHei", sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
h1 { text-align: center; color: #333; }
h2 { color: #444; border-bottom: 2px solid #eee; padding-bottom: 8px; }
h3 { color: #555; margin-top: 16px; }
.info { background: #f5f5f5; padding: 12px; border-radius: 6px; margin: 8px 0; }
.day-card { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 12px 0; }
.attraction { background: #e8f5e9; padding: 8px; border-radius: 4px; margin: 4px 0; }
.budget { background: #fff3e0; padding: 12px; border-radius: 6px; }
table { width: 100%; border-collapse: collapse; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th { background: #f0f0f0; }
</style>
</head>
<body>
""")

    html_parts.append(f"<h1>{plan.destination.name} 旅行计划</h1>")
    html_parts.append('<div class="info">')
    html_parts.append(f"<p><strong>日期:</strong> {plan.date_range.start_date} ~ {plan.date_range.end_date}</p>")
    if plan.description:
        html_parts.append(f"<p><strong>简介:</strong> {plan.description}</p>")
    html_parts.append("</div>")

    # 预算
    html_parts.append('<div class="budget">')
    html_parts.append("<h2>预算明细 (CNY)</h2>")
    html_parts.append("<table>")
    html_parts.append(f"<tr><td>景点门票</td><td>{plan.budget.attraction_tickets:.2f}</td></tr>")
    html_parts.append(f"<tr><td>酒店住宿</td><td>{plan.budget.hotel_accommodation:.2f}</td></tr>")
    html_parts.append(f"<tr><td>餐饮交通</td><td>{plan.budget.dining_transport:.2f}</td></tr>")
    html_parts.append(f"<tr><td>餐饮美食</td><td>{plan.budget.dining_food:.2f}</td></tr>")
    html_parts.append(f"<tr><th>总计</th><th>{plan.budget.total:.2f}</th></tr>")
    html_parts.append("</table></div>")

    # 每日行程
    html_parts.append("<h2>每日行程</h2>")
    for day in plan.daily_itineraries:
        html_parts.append('<div class="day-card">')
        html_parts.append(f"<h3>第 {day.day_index} 天 ({day.date}) — {day.summary}</h3>")

        if day.weather:
            temp = day.weather.temperature
            temp_str = f"{temp.low}~{temp.high}" if temp else "未知"
            html_parts.append(f"<p>天气: {day.weather.condition} {temp_str}°C</p>")

        if day.schedule:
            html_parts.append("<h4>日程安排</h4><table>")
            for slot in day.schedule:
                html_parts.append(f"<tr><td>{slot.start_time}-{slot.end_time}</td><td>{slot.activity}</td></tr>")
            html_parts.append("</table>")

        if day.attractions:
            html_parts.append("<h4>景点</h4>")
            for attr in day.attractions:
                html_parts.append(f'<div class="attraction"><strong>{attr.name}</strong> ({attr.play_duration})<br>{attr.description}</div>')

        if day.dining:
            html_parts.append(f"<p><strong>餐饮:</strong> 早餐={day.dining.breakfast} | 午餐={day.dining.lunch} | 晚餐={day.dining.dinner}</p>")

        if day.accommodation:
            html_parts.append(f"<p><strong>住宿:</strong> {day.accommodation.hotel_name} - {day.accommodation.room_type}</p>")

        html_parts.append("</div>")

    html_parts.append(f'<p style="text-align:center;color:#999;margin-top:20px;">创建时间: {plan.created_at}</p>')
    html_parts.append("</body></html>")

    return "".join(html_parts)
