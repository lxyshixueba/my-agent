"""旅行计划请求/响应模型."""

from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


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
    """旅行计划响应."""

    request_id: str = Field(..., description="请求唯一标识")
    destination: str = Field(..., description="目的地城市名称")
    days: int = Field(..., ge=1, description="出行天数")
    daily_itineraries: list[DailyItinerary] = Field(default_factory=list, description="每日行程安排")
    generated_at: str = Field(..., description="生成时间戳 ISO 8601")
