"""旅行计划生成与查询服务."""

import json
import logging
import uuid
from datetime import datetime, timezone, timedelta

from app.agents.travel_planner_agent import build_prompts
from app.config import settings
from app.models.travel_plan import (
    TravelPlanCreateRequest,
    TravelPlanResponse,
    TravelPlanFull,
    DestinationCity,
    DateRange,
    TravelPreferences,
    BudgetBreakdown,
    DailyItineraryDetail,
    TimeSlot,
    AttractionDetail,
    AccommodationPlan,
    DiningPlan,
    TransportationPlan,
    WeatherInfo,
    TemperatureRange,
    EditDayRequest,
)
from app.services.city_service import CityService
from app.services.llm_service import llm_service
from app.services.weather_service import weather_service
from app.services.unsplash_service import unsplash_service

logger = logging.getLogger("travel-helper")

# 实例化依赖
city_service = CityService()
# llm_service 已在 llm_service 模块中初始化为全局单例

# 内存存储（键为计划 ID 的 UUID 字符串，值为完整的 TravelPlanFull 对象）
_plans: dict[str, TravelPlanFull] = {}

# 重新规划任务状态追踪（键为计划 ID，值为 True 表示正在进行中）
_replan_in_progress: dict[str, bool] = {}


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

    # 将完整计划存入内存存储（T021）
    plan_id = str(uuid.uuid4())
    full_plan = _convert_to_full_plan(plan_id, request, plan_data)
    _plans[plan_id] = full_plan

    logger.info(f"旅行计划已存储 [id:{plan_id}]")
    return response


def get_travel_plan(plan_id: str) -> TravelPlanFull:
    """根据计划 ID 获取完整旅行计划数据.

    Args:
        plan_id: 旅行计划 UUID

    Returns:
        完整的旅行计划数据

    Raises:
        KeyError: 计划不存在时抛出
    """
    if plan_id not in _plans:
        raise KeyError(f"Travel plan not found: {plan_id}")
    return _plans[plan_id]


def _convert_to_full_plan(
    plan_id: str,
    request: TravelPlanCreateRequest,
    plan_data: dict,
) -> TravelPlanFull:
    """将 LLM 输出的 plan_data 转换为 TravelPlanFull 格式.

    Args:
        plan_id: 计划 UUID
        request: 原始创建请求
        plan_data: LLM 返回的原始 dict 数据

    Returns:
        完整的 TravelPlanFull 对象
    """
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz).isoformat()

    # 目的地城市（坐标暂时使用默认值 0.0，后续可由高德 MCP 服务补充）
    destination = DestinationCity(
        name=request.destination.name,
        latitude=0.0,
        longitude=0.0,
    )

    date_range = DateRange(
        start_date=request.start_date,
        end_date=request.end_date,
    )

    # 偏好
    preferences = TravelPreferences(
        accommodation_type=request.accommodation.value,
        transportation=request.transport_mode.value,
        tags=[p.value for p in request.preferences] if request.preferences else [],
        special_requests=request.special_requirements or "",
    )

    # 预算
    budget_data = plan_data.get("budget", {})
    budget = BudgetBreakdown(
        attraction_tickets=budget_data.get("attraction_tickets", 0),
        hotel_accommodation=budget_data.get("hotel_accommodation", 0),
        dining_transport=budget_data.get("dining_transport", 0),
        dining_food=budget_data.get("dining_food", 0),
        total=budget_data.get("total", 0),
    )

    # 每日行程
    daily_itineraries = []
    for day_data in plan_data.get("daily_itineraries", []):
        # 景点补充坐标
        attractions: list[AttractionDetail] = []
        for attr_data in day_data.get("attractions", []):
            attr_id = attr_data.get("id", str(uuid.uuid4())[:8])
            attractions.append(
                AttractionDetail(
                    id=attr_id,
                    name=attr_data.get("name", ""),
                    image_url=attr_data.get("image_url", ""),
                    play_duration=attr_data.get("play_duration", ""),
                    description=attr_data.get("description", ""),
                    features=attr_data.get("features", ""),
                    tips=attr_data.get("tips", ""),
                    latitude=attr_data.get("latitude", 0.0),
                    longitude=attr_data.get("longitude", 0.0),
                )
            )

        # 日程时间段
        schedule: list[TimeSlot] = []
        for slot_data in day_data.get("schedule", []):
            schedule.append(
                TimeSlot(
                    start_time=slot_data.get("start_time", slot_data.get("startTime", "")),
                    end_time=slot_data.get("end_time", slot_data.get("endTime", "")),
                    activity=slot_data.get("activity", ""),
                )
            )

        # 住宿
        accommodation: AccommodationPlan | None = None
        acc_data = day_data.get("accommodation")
        if acc_data:
            accommodation = AccommodationPlan(
                hotel_name=acc_data.get("hotel_name", ""),
                room_type=acc_data.get("room_type", ""),
                address=acc_data.get("address", ""),
                check_in=acc_data.get("check_in", acc_data.get("checkIn")),
                check_out=acc_data.get("check_out", acc_data.get("checkOut")),
                amenities=acc_data.get("amenities", ""),
                latitude=acc_data.get("latitude", 0.0),
                longitude=acc_data.get("longitude", 0.0),
            )

        # 餐饮
        dining: DiningPlan | None = None
        din_data = day_data.get("dining")
        if din_data:
            dining = DiningPlan(
                breakfast=din_data.get("breakfast", ""),
                lunch=din_data.get("lunch", ""),
                dinner=din_data.get("dinner", ""),
            )

        # 交通
        transportation: list[TransportationPlan] = []
        for trans_data in day_data.get("transportation", []):
            transportation.append(
                TransportationPlan(
                    type=trans_data.get("type", ""),
                    description=trans_data.get("description", ""),
                )
            )

        # 天气
        weather: WeatherInfo | None = None
        weather_data = day_data.get("weather")
        if weather_data:
            temp_range: TemperatureRange | None = None
            temp_data = weather_data.get("temperature")
            if temp_data:
                temp_range = TemperatureRange(
                    low=temp_data.get("low", 0),
                    high=temp_data.get("high", 0),
                )
            weather = WeatherInfo(
                date=weather_data.get("date", day_data.get("date", "")),
                condition=weather_data.get("condition", ""),
                temperature=temp_range,
                wind_speed=weather_data.get("wind_speed", weather_data.get("windSpeed", "微风")),
            )

        daily_itineraries.append(
            DailyItineraryDetail(
                day_index=day_data.get("day_index", day_data.get("dayIndex", 0)),
                date=day_data.get("date", ""),
                summary=day_data.get("summary", ""),
                schedule=schedule,
                attractions=attractions,
                accommodation=accommodation,
                dining=dining,
                transportation=transportation,
                weather=weather,
            )
        )

    description = plan_data.get("description", "")

    return TravelPlanFull(
        id=plan_id,
        destination=destination,
        date_range=date_range,
        description=description,
        preferences=preferences,
        budget=budget,
        daily_itineraries=daily_itineraries,
        created_at=now,
        updated_at=now,
    )


async def get_day_detail(plan_id: str, day_index: int) -> DailyItineraryDetail:
    """根据计划 ID 和 dayIndex 获取当日完整行程数据.

    按 dayIndex 筛选当日行程，补充天气数据和景点图片（通过 unsplash_service）。

    Args:
        plan_id: 旅行计划 UUID
        day_index: 第几天（从 1 开始）

    Returns:
        当日的完整行程数据（DailyItineraryDetail）

    Raises:
        KeyError: 计划不存在或未找到指定天的行程
    """
    # 获取完整旅行计划
    if plan_id not in _plans:
        raise KeyError(f"Travel plan not found: {plan_id}")

    full_plan = _plans[plan_id]

    # 按 dayIndex 筛选当日行程
    target_day = None
    for day in full_plan.daily_itineraries:
        if day.day_index == day_index:
            target_day = day
            break

    if target_day is None:
        raise KeyError(
            f"Day {day_index} not found in travel plan {plan_id}"
        )

    # 补充天气数据：如果当日没有缓存天气，尝试获取
    if target_day.weather is None and full_plan.destination.name:
        weather_data = await weather_service.get_weather(
            full_plan.destination.name,
            target_day.date,
        )
        if weather_data:
            from app.models.travel_plan import WeatherInfo, TemperatureRange

            temp_data = weather_data.get("temperature")
            temp_range = None
            if temp_data:
                temp_range = TemperatureRange(
                    low=temp_data.get("low", 0),
                    high=temp_data.get("high", 0),
                )

            target_day = target_day.model_copy(
                update={
                    "weather": WeatherInfo(
                        date=weather_data.get("date", target_day.date),
                        condition=weather_data.get("condition", ""),
                        temperature=temp_range,
                        wind_speed=weather_data.get("wind_speed", "微风"),
                    )
                }
            )

    # 补充景点图片：对没有图片的景点调用 unsplash_service 获取
    updated_attractions: list[AttractionDetail] = []
    for attr in target_day.attractions:
        if not attr.image_url or attr.image_url.strip() == "":
            image_url = await unsplash_service.search_image(attr.name)
            if image_url:
                updated_attractions.append(
                    attr.model_copy(update={"image_url": image_url})
                )
            else:
                updated_attractions.append(attr)
        else:
            updated_attractions.append(attr)

    # 如果有更新的景点列表，返回新的 DailyItineraryDetail
    if len(updated_attractions) != len(target_day.attractions) or any(
        a.image_url != b.image_url
        for a, b in zip(updated_attractions, target_day.attractions)
    ):
        target_day = target_day.model_copy(
            update={"attractions": updated_attractions}
        )

    return target_day


class EditDayValidationError(Exception):
    """编辑每日行程校验错误."""

    pass


def update_day_itinerary(
    plan_id: str,
    day_index: int,
    request: EditDayRequest,
) -> str:
    """更新指定天的行程数据.

    校验至少保留 1 个景点，更新 dailyItineraries 对应天的数据，更新 updatedAt。

    Args:
        plan_id: 旅行计划 UUID
        day_index: 第几天（从 1 开始）
        request: 编辑行程请求数据

    Returns:
        更新后的 updatedAt 时间戳（ISO 8601 格式）

    Raises:
        KeyError: 计划不存在或未找到指定天的行程
        EditDayValidationError: 校验失败（景点数为 0）
    """
    # 校验：至少保留 1 个景点
    if len(request.attractions) < 1:
        raise EditDayValidationError("至少保留 1 个景点")

    # 校验：day_index 范围
    if day_index < 1 or day_index > 30:
        raise EditDayValidationError("dayIndex 必须在 1-30 范围内")

    # 获取完整旅行计划
    if plan_id not in _plans:
        raise KeyError(f"Travel plan not found: {plan_id}")

    full_plan = _plans[plan_id]

    # 按 dayIndex 找到对应天的索引
    target_index = None
    for i, day in enumerate(full_plan.daily_itineraries):
        if day.day_index == day_index:
            target_index = i
            break

    if target_index is None:
        raise KeyError(
            f"Day {day_index} not found in travel plan {plan_id}"
        )

    # 获取旧的行程数据（用于保留未更新的字段）
    old_day = full_plan.daily_itineraries[target_index]

    # 构建更新后的 DailyItineraryDetail
    # 使用 model_copy 创建新对象，保留未提供的字段
    updated_day = old_day.model_copy(
        update={
            "schedule": request.schedule,
            "attractions": request.attractions,
            "accommodation": request.accommodation,
            "dining": request.dining,
            "transportation": request.transportation,
        }
    )

    # 更新内存存储中的行程
    full_plan.daily_itineraries[target_index] = updated_day

    # 更新 updatedAt 时间戳
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz).isoformat()
    full_plan.updated_at = now

    logger.info(f"行程更新成功 [plan:{plan_id}] day:{day_index} [updated_at:{now}]")

    return now


class ReplanConflictError(Exception):
    """重新规划任务冲突（已有任务在进行中）."""

    pass


async def replan_travel_plan(
    plan_id: str,
    edit_traces: str = "",
    new_constraints: str = "",
) -> dict:
    """触发行程重新规划.

    调用 LangGraph StateGraph 执行重新规划流程：收集上下文 -> 调用 LLM -> 返回新行程。

    Args:
        plan_id: 旅行计划 UUID
        edit_traces: 用户编辑痕迹
        new_constraints: 新增约束条件

    Returns:
        包含 message 和 estimatedTime 的字典

    Raises:
        KeyError: 计划不存在时抛出
        ReplanConflictError: 已有重新规划任务在进行中时抛出
    """
    # 检查计划是否存在
    if plan_id not in _plans:
        raise KeyError(f"Travel plan not found: {plan_id}")

    # 检查是否已有重新规划任务在进行中
    if _replan_in_progress.get(plan_id, False):
        raise ReplanConflictError("A replanning task is already in progress")

    full_plan = _plans[plan_id]

    # 标记为正在进行中
    _replan_in_progress[plan_id] = True

    try:
        # 将当前行程序列化为 JSON 供 LLM 参考
        current_itinerary_json = json.dumps(
            {
                "daily_itineraries": [
                    day.model_dump(by_alias=True) for day in full_plan.daily_itineraries
                ],
                "budget": full_plan.budget.model_dump(by_alias=True),
            },
            ensure_ascii=False,
            indent=2,
        )

        # 获取 LangGraph StateGraph 实例
        from app.agents.itinerary_agent import get_replan_graph

        graph = get_replan_graph()

        # 构建初始状态
        from app.agents.itinerary_agent import ReplanState

        initial_state = {
            "plan_id": plan_id,
            "destination": full_plan.destination.name,
            "days": len(full_plan.daily_itineraries),
            "start_date": full_plan.date_range.start_date.isoformat()
            if hasattr(full_plan.date_range.start_date, "isoformat")
            else str(full_plan.date_range.start_date),
            "end_date": full_plan.date_range.end_date.isoformat()
            if hasattr(full_plan.date_range.end_date, "isoformat")
            else str(full_plan.date_range.end_date),
            "transport": full_plan.preferences.transportation if full_plan.preferences else "",
            "accommodation": full_plan.preferences.accommodation_type if full_plan.preferences else "",
            "preferences": full_plan.preferences.tags if full_plan.preferences else [],
            "special_requests": full_plan.preferences.special_requests if full_plan.preferences else "",
            "current_itinerary": current_itinerary_json,
            "edit_traces": edit_traces,
            "new_constraints": new_constraints,
        }

        logger.info(f"[replan] 开始重新规划 [plan:{plan_id}]")

        # 执行 StateGraph
        result = await graph.ainvoke(initial_state)

        # 检查结果
        if result.get("error"):
            error_msg = result["error"]
            logger.error(f"[replan] 重新规划失败 [plan:{plan_id}]: {error_msg}")
            raise RuntimeError(f"重新规划失败: {error_msg}")

        parsed_result = result.get("result")
        if not parsed_result:
            raise RuntimeError("重新规划返回空结果")

        # 将新行程更新到内存存储
        tz = timezone(timedelta(hours=8))
        now = datetime.now(tz).isoformat()

        # 使用已有的 _convert_to_full_plan 辅助逻辑更新
        # 由于 _convert_to_full_plan 需要 TravelPlanCreateRequest，我们直接手动更新
        new_daily_itineraries = []
        for day_data in parsed_result.get("daily_itineraries", []):
            # 解析景点
            attractions: list[AttractionDetail] = []
            for attr_data in day_data.get("attractions", []):
                attractions.append(
                    AttractionDetail(
                        id=attr_data.get("id", str(uuid.uuid4())[:8]),
                        name=attr_data.get("name", ""),
                        image_url=attr_data.get("image_url", ""),
                        play_duration=attr_data.get("play_duration", ""),
                        description=attr_data.get("description", ""),
                        features=attr_data.get("features", ""),
                        tips=attr_data.get("tips", ""),
                        latitude=attr_data.get("latitude", 0.0),
                        longitude=attr_data.get("longitude", 0.0),
                    )
                )

            # 解析时间段
            schedule: list[TimeSlot] = []
            for slot_data in day_data.get("schedule", []):
                schedule.append(
                    TimeSlot(
                        start_time=slot_data.get("start_time", slot_data.get("startTime", "")),
                        end_time=slot_data.get("end_time", slot_data.get("endTime", "")),
                        activity=slot_data.get("activity", ""),
                    )
                )

            # 解析住宿
            accommodation: AccommodationPlan | None = None
            acc_data = day_data.get("accommodation")
            if acc_data:
                accommodation = AccommodationPlan(
                    hotel_name=acc_data.get("hotel_name", ""),
                    room_type=acc_data.get("room_type", ""),
                    address=acc_data.get("address", ""),
                    check_in=acc_data.get("check_in", acc_data.get("checkIn")),
                    check_out=acc_data.get("check_out", acc_data.get("checkOut")),
                    amenities=acc_data.get("amenities", ""),
                    latitude=acc_data.get("latitude", 0.0),
                    longitude=acc_data.get("longitude", 0.0),
                )

            # 解析餐饮
            dining: DiningPlan | None = None
            din_data = day_data.get("dining")
            if din_data:
                dining = DiningPlan(
                    breakfast=din_data.get("breakfast", ""),
                    lunch=din_data.get("lunch", ""),
                    dinner=din_data.get("dinner", ""),
                )

            # 解析交通
            transportation: list[TransportationPlan] = []
            for trans_data in day_data.get("transportation", []):
                transportation.append(
                    TransportationPlan(
                        type=trans_data.get("type", ""),
                        description=trans_data.get("description", ""),
                    )
                )

            # 解析天气
            weather: WeatherInfo | None = None
            weather_data = day_data.get("weather")
            if weather_data:
                temp_data = weather_data.get("temperature")
                temp_range = None
                if temp_data:
                    temp_range = TemperatureRange(
                        low=temp_data.get("low", 0),
                        high=temp_data.get("high", 0),
                    )
                weather = WeatherInfo(
                    date=weather_data.get("date", day_data.get("date", "")),
                    condition=weather_data.get("condition", ""),
                    temperature=temp_range,
                    wind_speed=weather_data.get("wind_speed", weather_data.get("windSpeed", "微风")),
                )

            new_daily_itineraries.append(
                DailyItineraryDetail(
                    day_index=day_data.get("day_index", day_data.get("dayIndex", 0)),
                    date=day_data.get("date", ""),
                    summary=day_data.get("summary", ""),
                    schedule=schedule,
                    attractions=attractions,
                    accommodation=accommodation,
                    dining=dining,
                    transportation=transportation,
                    weather=weather,
                )
            )

        # 更新预算
        budget_data = parsed_result.get("budget", {})
        new_budget = BudgetBreakdown(
            attraction_tickets=budget_data.get("attraction_tickets", full_plan.budget.attraction_tickets),
            hotel_accommodation=budget_data.get("hotel_accommodation", full_plan.budget.hotel_accommodation),
            dining_transport=budget_data.get("dining_transport", full_plan.budget.dining_transport),
            dining_food=budget_data.get("dining_food", full_plan.budget.dining_food),
        )

        # 更新完整计划
        full_plan.daily_itineraries = new_daily_itineraries
        full_plan.budget = new_budget
        full_plan.updated_at = now
        full_plan.description = parsed_result.get("description", full_plan.description)

        logger.info(f"[replan] 重新规划成功 [plan:{plan_id}] [updated_at:{now}]")

        return {
            "message": "Replanning completed successfully",
            "estimatedTime": "已完成",
        }

    except ReplanConflictError:
        # 冲突错误不需要清除状态（因为根本没设置）
        raise
    except Exception:
        # 其他异常，清除进行中状态
        _replan_in_progress[plan_id] = False
        raise
    finally:
        # 正常完成也清除状态
        if _replan_in_progress.get(plan_id, False):
            _replan_in_progress[plan_id] = False
