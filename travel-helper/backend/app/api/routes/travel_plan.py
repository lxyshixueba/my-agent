"""旅行计划 API 路由."""

import logging
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import Response

from app.models.travel_plan import TravelPlanCreateRequest, TravelPlanResponse, TravelPlanFull, DailyItineraryDetail, EditDayRequest, ReplanRequest
from app.services.city_service import city_service
from app.services.travel_plan_service import (
    generate_travel_plan,
    get_travel_plan,
    get_day_detail,
    validate_request,
    update_day_itinerary,
    replan_travel_plan,
    TravelPlanValidationError,
    EditDayValidationError,
    ReplanConflictError,
)
from app.services.export_service import generate_text_export, generate_html_export

logger = logging.getLogger("travel-helper")

router = APIRouter(tags=["旅行计划"])


@router.post(
    "/travel-plans/generate",
    response_model=TravelPlanResponse,
    summary="生成旅行计划",
)
async def create_travel_plan(body: TravelPlanCreateRequest):
    """基于用户输入生成个性化旅行计划.

    - 校验目的地、日期、偏好
    - 调用 LLM 生成旅行计划
    - 返回结构化的行程结果
    """
    try:
        validate_request(body)
    except TravelPlanValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        return await generate_travel_plan(body)
    except RuntimeError as e:
        logger.error(f"旅行计划生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/travel-plans/{plan_id}",
    response_model=TravelPlanFull,
    summary="获取旅行计划详情",
)
async def get_travel_plan_endpoint(plan_id: str):
    """获取指定旅行计划的完整数据.

    Args:
        plan_id: 旅行计划 UUID

    Returns:
        完整的旅行计划数据（含预算、地图坐标、每日行程详情等）

    Raises:
        404: 计划不存在
    """
    try:
        plan = get_travel_plan(plan_id)
        return plan
    except KeyError:
        raise HTTPException(status_code=404, detail="Travel plan not found")


@router.get(
    "/travel-plans/{plan_id}/day/{day_index}",
    response_model=DailyItineraryDetail,
    summary="获取当日行程详情",
)
async def get_day_detail_endpoint(plan_id: str, day_index: int):
    """获取指定旅行计划中某一天的完整行程数据.

    Args:
        plan_id: 旅行计划 UUID
        day_index: 第几天（从 1 开始）

    Returns:
        当日的完整行程数据（含景点、住宿、餐饮、交通、天气等）

    Raises:
        404: 计划不存在或未找到指定天的行程
        400: dayIndex 无效
    """
    if day_index < 1:
        raise HTTPException(status_code=400, detail="dayIndex must be >= 1")

    try:
        day = await get_day_detail(plan_id, day_index)
        return day
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/travel-plans/{plan_id}/day/{day_index}",
    summary="编辑每日行程",
)
async def update_day_itinerary_endpoint(
    plan_id: str,
    day_index: int,
    request: EditDayRequest,
):
    """更新指定天的行程数据（景点顺序调整、景点删除等）.

    Args:
        plan_id: 旅行计划 UUID
        day_index: 第几天（从 1 开始）
        request: 编辑行程请求数据

    Returns:
        更新结果（message, dayIndex, updatedAt）

    Raises:
        404: 计划不存在或未找到指定天的行程
        400: 校验失败（景点数为 0）
    """
    if day_index < 1:
        raise HTTPException(status_code=400, detail="dayIndex must be >= 1")

    try:
        updated_at = update_day_itinerary(plan_id, day_index, request)
        return {
            "message": "Day itinerary updated successfully",
            "dayIndex": day_index,
            "updatedAt": updated_at,
        }
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except EditDayValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/travel-plans/{plan_id}/replan",
    summary="重新规划行程",
)
async def replan_travel_plan_endpoint(
    plan_id: str,
    request: ReplanRequest,
):
    """触发重新生成旅行计划.

    调用 LangGraph StateGraph 执行重新规划流程：收集上下文 -> 调用 LLM -> 返回新行程。
    如果已有重新规划任务在进行中，返回 409 Conflict。

    Args:
        plan_id: 旅行计划 UUID
        request: 重新规划请求（包含编辑痕迹和新增约束）

    Returns:
        { message, estimatedTime }

    Raises:
        404: 计划不存在
        409: 已有重新规划任务在进行中
        500: 重新规划失败
    """
    try:
        result = await replan_travel_plan(
            plan_id=plan_id,
            edit_traces=request.edit_traces,
            new_constraints=request.new_constraints,
        )
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Travel plan not found")
    except ReplanConflictError:
        raise HTTPException(
            status_code=409,
            detail="A replanning task is already in progress",
        )
    except RuntimeError as e:
        logger.error(f"重新规划失败 [plan:{plan_id}]: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


@router.get(
    "/travel-plans/{plan_id}/export",
    summary="导出旅行计划",
)
async def export_travel_plan(
    plan_id: str,
    fmt: str = Query(default="text", description="导出格式: text / html"),
):
    """获取旅行计划的导出内容.

    前端可基于返回内容生成图片或 PDF。

    Args:
        plan_id: 旅行计划 UUID
        fmt: 导出格式（text=纯文本, html=HTML 格式）

    Returns:
        导出内容（纯文本或 HTML）

    Raises:
        404: 计划不存在
        400: 格式无效
    """
    try:
        plan = get_travel_plan(plan_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Travel plan not found")

    if fmt not in ("text", "html"):
        raise HTTPException(
            status_code=400,
            detail="Invalid format. Use 'text' or 'html'",
        )

    if fmt == "text":
        content = generate_text_export(plan)
        return Response(content=content, media_type="text/plain; charset=utf-8")
    else:
        content = generate_html_export(plan)
        return Response(content=content, media_type="text/html; charset=utf-8")
