"""旅行计划请求/响应模型."""

from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class TransportMode(str, Enum):
    """出行交通方式."""

    flight = "flight"  # 飞机
    high_speed_rail = "high_speed_rail"  # 高铁
    self_driving = "self_driving"  # 自驾
    bus = "bus"  # 大巴


class Accommodation(str, Enum):
    """住宿偏好."""

    economy = "economy"  # 经济型酒店
    comfort = "comfort"  # 舒适型酒店
    premium = "premium"  # 高档型酒店
    luxury = "luxury"  # 豪华酒店
    homestay = "homestay"  # 民宿


class PreferenceTag(str, Enum):
    """旅行偏好标签."""

    sightseeing = "sightseeing"  # 景点观光
    food = "food"  # 美食
    nature = "nature"  # 自然风光
    history_culture = "history_culture"  # 历史文化
    shopping = "shopping"  # 购物体验
    adventure = "adventure"  # 探险
    cultural_experience = "cultural_experience"  # 文化体验
    leisure_entertainment = "leisure_entertainment"  # 休闲娱乐


class CityRef(BaseModel):
    """目的地城市引用."""

    name: str = Field(..., min_length=1, description="城市名称")
    code: str = Field(..., min_length=1, description="城市编码")


class TravelPlanCreateRequest(BaseModel):
    """旅行计划创建请求."""

    destination: CityRef
    start_date: date
    end_date: date
    transport_mode: TransportMode
    accommodation: Accommodation
    preferences: Optional[list[PreferenceTag]] = None
    special_requirements: Optional[str] = Field(None, max_length=500)

    @field_validator("end_date")
    @classmethod
    def end_date_must_be_after_start(cls, v: date, info) -> date:
        start = info.data.get("start_date")
        if start and v < start:
            raise ValueError("返回日期不能早于出发日期")
        return v

    @field_validator("start_date")
    @classmethod
    def start_date_must_be_future(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("出发日期不能早于今天")
        return v

    @property
    def days(self) -> int:
        """计算出行天数."""
        return (self.end_date - self.start_date).days + 1


class Activity(BaseModel):
    """行程活动."""

    type: str = Field(..., description="活动类型: attraction/restaurant/shopping/activity")
    name: str = Field(..., description="活动名称")
    description: str = Field(..., description="活动描述")
    time_slot: str = Field(..., description="建议时段: morning/afternoon/evening")
    duration_minutes: int = Field(..., description="预计耗时（分钟）")


class DailyItinerary(BaseModel):
    """每日行程."""

    day: int = Field(..., ge=1, description="第几天")
    date: str = Field(..., description="具体日期 ISO 8601")
    theme: str = Field(..., description="当日主题")
    activities: list[Activity] = Field(default_factory=list, description="活动列表")


class TravelPlanResponse(BaseModel):
    """旅行计划响应（001 模块原始响应格式）."""

    request_id: str = Field(..., description="请求唯一标识")
    destination: str = Field(..., description="目的地城市名称")
    days: int = Field(..., ge=1, description="出行天数")
    daily_itineraries: list[DailyItinerary] = Field(default_factory=list, description="每日行程安排")
    generated_at: str = Field(..., description="生成时间戳 ISO 8601")


from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """带 camelCase 别名序列化的基础模型（用于 002 模块）."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


# =============================================================================
# 002 模块 — 旅行计划详情完整数据模型（与 data-model.md 对齐）
# =============================================================================


class DestinationCity(CamelModel):
    """目的地城市（含地图坐标）."""

    name: str = Field(..., min_length=1, description="城市名称")
    latitude: float = Field(default=0.0, description="纬度")
    longitude: float = Field(default=0.0, description="经度")


class DateRange(CamelModel):
    """出行起止日期."""

    start_date: date = Field(..., description="出发日期")
    end_date: date = Field(..., description="返回日期")


class TravelPreferences(CamelModel):
    """旅行偏好."""

    accommodation_type: str = Field(default="", description="住宿偏好")
    transportation: str = Field(default="", description="交通方式")
    tags: list[str] = Field(default_factory=list, description="偏好标签")
    special_requests: str = Field(default="", description="特殊服务要求")


class BudgetBreakdown(CamelModel):
    """预算明细."""

    attraction_tickets: float = Field(..., description="景点门票预算（CNY）")
    hotel_accommodation: float = Field(..., description="酒店住宿预算（CNY）")
    dining_transport: float = Field(..., description="餐饮交通预算（CNY）")
    dining_food: float = Field(..., description="餐饮美食预算（CNY）")
    total: float = Field(default=0.0, description="预估总费用（CNY），自动计算")

    @model_validator(mode="after")
    def auto_calculate_total(self) -> "BudgetBreakdown":
        """自动计算预算总额（允许 ±0.01 浮点误差）."""
        if self.total == 0:
            self.total = round(
                self.attraction_tickets
                + self.hotel_accommodation
                + self.dining_transport
                + self.dining_food,
                2,
            )
        return self


class TimeSlot(CamelModel):
    """时间段."""

    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="开始时间（HH:mm）")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="结束时间（HH:mm）")
    activity: str = Field(..., description="活动描述")


class AttractionDetail(CamelModel):
    """景点详情（含地图坐标）."""

    id: str = Field(..., description="景点唯一标识（UUID）")
    name: str = Field(..., min_length=1, description="景点名称")
    image_url: str = Field(default="", description="景点图片 URL")
    play_duration: str = Field(default="", description="游玩时间")
    description: str = Field(default="", description="详细描述")
    features: str = Field(default="", description="景点特色")
    tips: str = Field(default="", description="推荐信息")
    latitude: float = Field(default=0.0, description="景点纬度")
    longitude: float = Field(default=0.0, description="景点经度")


class AccommodationPlan(CamelModel):
    """住宿安排（含地图坐标）."""

    hotel_name: str = Field(default="", description="酒店名称")
    room_type: str = Field(default="", description="房型")
    address: str = Field(default="", description="地址")
    check_in: Optional[str] = Field(default=None, description="入住日期")
    check_out: Optional[str] = Field(default=None, description="退房日期")
    amenities: str = Field(default="", description="设施描述")
    latitude: float = Field(default=0.0, description="酒店纬度")
    longitude: float = Field(default=0.0, description="酒店经度")


class DiningPlan(CamelModel):
    """餐饮安排."""

    breakfast: str = Field(default="", description="早餐推荐")
    lunch: str = Field(default="", description="午餐推荐")
    dinner: str = Field(default="", description="晚餐推荐")


class TemperatureRange(CamelModel):
    """温度范围."""

    low: int = Field(..., description="最低温度")
    high: int = Field(..., description="最高温度")


class WeatherInfo(CamelModel):
    """天气信息."""

    date: str = Field(..., description="天气日期")
    condition: str = Field(..., description="天气状况")
    temperature: Optional[TemperatureRange] = Field(default=None, description="温度范围")
    wind_speed: str = Field(default="微风", description="风速")


class TransportationPlan(CamelModel):
    """交通安排."""

    type: str = Field(..., description="交通类型")
    description: str = Field(..., description="交通描述")


class DailyItineraryDetail(CamelModel):
    """每日行程详情（002 模块完整格式）."""

    day_index: int = Field(..., ge=1, le=30, description="第几天（1-30）")
    date: str = Field(..., description="具体日期（YYYY-MM-DD）")
    summary: str = Field(..., description="行程概要")
    schedule: list[TimeSlot] = Field(default_factory=list, description="日程时间线")
    attractions: list[AttractionDetail] = Field(default_factory=list, description="景点列表")
    accommodation: Optional[AccommodationPlan] = Field(default=None, description="住宿安排")
    dining: Optional[DiningPlan] = Field(default=None, description="餐饮安排")
    transportation: list[TransportationPlan] = Field(default_factory=list, description="交通安排")
    weather: Optional[WeatherInfo] = Field(default=None, description="天气信息")


class EditDayRequest(CamelModel):
    """编辑每日行程请求体."""

    schedule: list[TimeSlot] = Field(default_factory=list, description="日程时间线")
    attractions: list[AttractionDetail] = Field(default_factory=list, description="景点列表")
    accommodation: Optional[AccommodationPlan] = Field(default=None, description="住宿安排")
    dining: Optional[DiningPlan] = Field(default=None, description="餐饮安排")
    transportation: list[TransportationPlan] = Field(default_factory=list, description="交通安排")


class ReplanRequest(CamelModel):
    """重新规划行程请求体."""

    edit_traces: str = Field(default="", description="用户编辑痕迹（如'删除了第2天的故宫'）")
    new_constraints: str = Field(default="", description="新增约束条件")


class TravelPlanFull(CamelModel):
    """旅行计划完整响应（002 模块，含预算、地图坐标、天气等全部字段）."""

    id: str = Field(..., description="计划唯一标识符（UUID）")
    destination: DestinationCity = Field(..., description="目的地城市")
    date_range: DateRange = Field(..., description="出行起止日期")
    description: str = Field(default="", description="计划简介")
    preferences: Optional[TravelPreferences] = Field(default=None, description="用户偏好")
    budget: BudgetBreakdown = Field(..., description="预算明细")
    daily_itineraries: list[DailyItineraryDetail] = Field(
        default_factory=list,
        description="每日行程列表",
    )
    created_at: str = Field(..., description="计划创建时间")
    updated_at: str = Field(..., description="最后更新时间")
