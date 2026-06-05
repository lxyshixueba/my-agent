"""GET /api/v1/travel-plans/{id} API 合约测试.

验证端点返回的数据结构符合 contracts/api-contract.md 定义的格式。
"""

import pytest
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def client():
    """创建异步 HTTP 客户端."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def valid_plan_id():
    """生成一个有效的计划 ID（直接写入内存存储）."""
    from app.services.travel_plan_service import _plans, TravelPlanFull
    from app.models.travel_plan import (
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
    )

    plan_id = "test-plan-001-uuid"

    budget = BudgetBreakdown(
        attraction_tickets=1130,
        hotel_accommodation=1200,
        dining_transport=730,
        dining_food=300,
        total=3360,
    )

    daily_itineraries = [
        DailyItineraryDetail(
            day_index=1,
            date="2026-07-01",
            summary="故宫 - 鸟巢一日游",
            schedule=[
                TimeSlot(
                    start_time="08:00",
                    end_time="10:00",
                    activity="前往故宫并游览",
                ),
                TimeSlot(
                    start_time="10:30",
                    end_time="12:00",
                    activity="继续游览故宫",
                ),
                TimeSlot(
                    start_time="13:00",
                    end_time="15:00",
                    activity="前往鸟巢游览",
                ),
            ],
            attractions=[
                AttractionDetail(
                    id="uuid-1",
                    name="北京故宫",
                    image_url="https://images.unsplash.com/example",
                    play_duration="2-3小时",
                    description="中国明清两代的皇家宫殿",
                    features="世界文化遗产",
                    tips="建议提前网上购票",
                    latitude=39.9163,
                    longitude=116.3972,
                ),
            ],
            accommodation=AccommodationPlan(
                hotel_name="北京万豪酒店",
                room_type="豪华标准间",
                address="北京市朝阳区xxx路xxx号",
                check_in="2026-07-01",
                check_out="2026-07-03",
                amenities="免费WiFi、停车位、商务中心、健身房",
                latitude=39.9200,
                longitude=116.4100,
            ),
            dining=DiningPlan(
                breakfast="北京传统早餐 豆浆油条、煎饼果子等",
                lunch="北京烤鸭 全聚德或便宜坊的招牌菜",
                dinner="北京炸酱面 老北京炸酱面是经典的北京小吃",
            ),
            transportation=[
                TransportationPlan(
                    type="地铁",
                    description="地铁1号线 天安门东站 → 奥林匹克公园站",
                ),
            ],
            weather=WeatherInfo(
                date="2026-07-01",
                condition="晴",
                temperature=TemperatureRange(low=5, high=15),
                wind_speed="微风",
            ),
        ),
    ]

    plan = TravelPlanFull(
        id=plan_id,
        destination=DestinationCity(
            name="北京",
            latitude=39.9042,
            longitude=116.4074,
        ),
        date_range=DateRange(
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 15),
        ),
        description="旅行计划包含15天行程",
        preferences=TravelPreferences(
            accommodation_type="高档型酒店",
            transportation="高铁",
            tags=["景点观光", "美食"],
            special_requests="",
        ),
        budget=budget,
        daily_itineraries=daily_itineraries,
        created_at="2026-06-01T10:00:00+08:00",
        updated_at="2026-06-01T10:00:00+08:00",
    )

    _plans[plan_id] = plan
    return plan_id


class TestGetTravelPlanContract:
    """GET /api/v1/travel-plans/{id} 合约测试."""

    async def test_valid_plan_returns_200(self, client, valid_plan_id):
        """有效的计划 ID 返回 200 OK."""
        response = await client.get(f"/api/v1/travel-plans/{valid_plan_id}")
        assert response.status_code == 200

    async def test_response_has_required_fields(self, client, valid_plan_id):
        """响应包含所有必填字段."""
        response = await client.get(f"/api/v1/travel-plans/{valid_plan_id}")
        data = response.json()

        # 顶层必填字段
        assert "id" in data
        assert "destination" in data
        assert "dateRange" in data
        assert "budget" in data
        assert "dailyItineraries" in data
        assert "createdAt" in data
        assert "updatedAt" in data

    async def test_destination_structure(self, client, valid_plan_id):
        """destination 包含 name, latitude, longitude."""
        response = await client.get(f"/api/v1/travel-plans/{valid_plan_id}")
        data = response.json()

        dest = data["destination"]
        assert "name" in dest
        assert "latitude" in dest
        assert "longitude" in dest
        assert dest["name"] == "北京"

    async def test_date_range_structure(self, client, valid_plan_id):
        """dateRange 包含 startDate, endDate."""
        response = await client.get(f"/api/v1/travel-plans/{valid_plan_id}")
        data = response.json()

        dr = data["dateRange"]
        assert "startDate" in dr
        assert "endDate" in dr

    async def test_budget_structure(self, client, valid_plan_id):
        """budget 包含所有分类金额和 total."""
        response = await client.get(f"/api/v1/travel-plans/{valid_plan_id}")
        data = response.json()

        budget = data["budget"]
        assert "attractionTickets" in budget
        assert "hotelAccommodation" in budget
        assert "diningTransport" in budget
        assert "diningFood" in budget
        assert "total" in budget

    async def test_daily_itineraries_structure(self, client, valid_plan_id):
        """dailyItineraries 每项包含 dayIndex, date, summary, schedule, attractions 等."""
        response = await client.get(f"/api/v1/travel-plans/{valid_plan_id}")
        data = response.json()

        itineraries = data["dailyItineraries"]
        assert isinstance(itineraries, list)
        assert len(itineraries) > 0

        day = itineraries[0]
        assert "dayIndex" in day
        assert "date" in day
        assert "summary" in day
        assert "schedule" in day
        assert "attractions" in day

    async def test_attraction_detail_structure(self, client, valid_plan_id):
        """景点详情包含 id, name, imageUrl, playDuration 等字段."""
        response = await client.get(f"/api/v1/travel-plans/{valid_plan_id}")
        data = response.json()

        attractions = data["dailyItineraries"][0]["attractions"]
        assert len(attractions) > 0

        attr = attractions[0]
        assert "id" in attr
        assert "name" in attr
        assert "imageUrl" in attr
        assert "playDuration" in attr
        assert "description" in attr
        assert "features" in attr
        assert "latitude" in attr
        assert "longitude" in attr

    async def test_nonexistent_plan_returns_404(self, client):
        """不存在的计划 ID 返回 404."""
        response = await client.get("/api/v1/travel-plans/nonexistent-id")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    async def test_preferences_structure(self, client, valid_plan_id):
        """preferences 包含 accommodationType, transportation, tags, specialRequests."""
        response = await client.get(f"/api/v1/travel-plans/{valid_plan_id}")
        data = response.json()

        prefs = data["preferences"]
        assert "accommodationType" in prefs
        assert "transportation" in prefs
        assert "tags" in prefs
        assert "specialRequests" in prefs

    async def test_schedule_time_slots(self, client, valid_plan_id):
        """schedule 时间段包含 startTime, endTime, activity."""
        response = await client.get(f"/api/v1/travel-plans/{valid_plan_id}")
        data = response.json()

        schedule = data["dailyItineraries"][0]["schedule"]
        assert len(schedule) > 0

        slot = schedule[0]
        assert "startTime" in slot
        assert "endTime" in slot
        assert "activity" in slot

    async def test_weather_structure(self, client, valid_plan_id):
        """weather 包含 date, condition, temperature, windSpeed."""
        response = await client.get(f"/api/v1/travel-plans/{valid_plan_id}")
        data = response.json()

        weather = data["dailyItineraries"][0]["weather"]
        assert "date" in weather
        assert "condition" in weather
        assert "temperature" in weather
        assert "windSpeed" in weather
        assert "low" in weather["temperature"]
        assert "high" in weather["temperature"]
