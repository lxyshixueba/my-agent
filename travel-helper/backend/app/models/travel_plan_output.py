"""旅行计划结构化输出模型（LangChain with_structured_output）."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class AttractionOutput(BaseModel):
    """景点结构化输出."""

    id: str = Field(..., description="景点唯一标识（UUID）")
    name: str = Field(..., description="景点名称")
    play_duration: str = Field(..., description="游玩时间，如'2-3小时'")
    description: str = Field(..., description="景点详细描述")
    features: str = Field(..., description="景点特色")
    tips: str = Field(default="", description="游览建议/小贴士")
    latitude: float = Field(default=0.0, description="景点纬度")
    longitude: float = Field(default=0.0, description="景点经度")


class TimeSlotOutput(BaseModel):
    """时间段输出."""

    start_time: str = Field(..., description="开始时间（HH:mm）")
    end_time: str = Field(..., description="结束时间（HH:mm）")
    activity: str = Field(..., description="活动描述")


class AccommodationOutput(BaseModel):
    """住宿输出."""

    hotel_name: str = Field(..., description="酒店名称")
    room_type: str = Field(..., description="房型")
    address: str = Field(..., description="酒店地址")
    amenities: str = Field(
        default="", description="设施描述，如'免费WiFi、游泳池、健身房'"
    )
    latitude: float = Field(default=0.0, description="酒店纬度")
    longitude: float = Field(default=0.0, description="酒店经度")


class DiningOutput(BaseModel):
    """餐饮输出."""

    breakfast: str = Field(..., description="早餐推荐")
    lunch: str = Field(..., description="午餐推荐")
    dinner: str = Field(..., description="晚餐推荐")


class TransportationOutput(BaseModel):
    """交通输出."""

    type: str = Field(..., description="交通类型，如'地铁'/'公交'/'出租车'")
    description: str = Field(..., description="交通描述")


class WeatherOutput(BaseModel):
    """天气输出."""

    date: str = Field(..., description="日期（YYYY-MM-DD）")
    condition: str = Field(..., description="天气状况，如'晴'/'多云'/'雨'")
    temp_low: int = Field(..., description="最低温度")
    temp_high: int = Field(..., description="最高温度")
    wind_speed: str = Field(default="微风", description="风速")


class BudgetOutput(BaseModel):
    """预算输出."""

    attraction_tickets: float = Field(..., description="景点门票预算（CNY）")
    hotel_accommodation: float = Field(..., description="酒店住宿预算（CNY）")
    dining_transport: float = Field(..., description="餐饮交通预算（CNY）")
    dining_food: float = Field(..., description="餐饮美食预算（CNY）")
    total: float = Field(..., description="预估总费用（CNY）")


class DailyItineraryOutput(BaseModel):
    """每日行程输出."""

    day_index: int = Field(..., ge=1, le=30, description="第几天（1-30）")
    date: str = Field(..., description="具体日期（YYYY-MM-DD）")
    summary: str = Field(..., description="当日行程概要")
    schedule: list[TimeSlotOutput] = Field(
        default_factory=list, description="时间段列表"
    )
    attractions: list[AttractionOutput] = Field(
        default_factory=list, description="景点列表（1-10个）"
    )
    accommodation: Optional[AccommodationOutput] = Field(
        default=None, description="住宿安排"
    )
    dining: Optional[DiningOutput] = Field(default=None, description="餐饮安排")
    transportation: list[TransportationOutput] = Field(
        default_factory=list, description="交通安排"
    )
    weather: Optional[WeatherOutput] = Field(default=None, description="天气信息")


class TravelPlanOutput(BaseModel):
    """旅行计划完整结构化输出."""

    destination_name: str = Field(..., description="目的地城市名称")
    destination_latitude: float = Field(
        default=0.0, description="目的地纬度（估算值）"
    )
    destination_longitude: float = Field(
        default=0.0, description="目的地经度（估算值）"
    )
    description: str = Field(..., description="旅行计划简介")
    budget: BudgetOutput = Field(..., description="预算明细")
    daily_itineraries: list[DailyItineraryOutput] = Field(
        default_factory=list, description="每日行程列表"
    )
