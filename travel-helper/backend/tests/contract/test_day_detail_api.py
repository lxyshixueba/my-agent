"""GET /api/v1/travel-plans/{id}/day/{dayIndex} API 合约测试.

验证端点返回的单日行程数据结构符合 contracts/api-contract.md 定义的格式。
"""

import pytest
from datetime import date
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def client():
    """创建异步 HTTP 客户端."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def plan_with_multiple_days():
    """创建一个包含多日行程的测试计划并写入内存存储."""
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

    plan_id = "test-day-detail-plan-001"

    budget = BudgetBreakdown(
        attraction_tickets=2260,
        hotel_accommodation=2400,
        dining_transport=1460,
        dining_food=600,
        total=6720,
    )

    daily_itineraries = []

    # 第 1 天行程
    day1 = DailyItineraryDetail(
        day_index=1,
        date="2026-07-01",
        summary="故宫 - 鸟巢一日游",
        schedule=[
            TimeSlot(start_time="08:00", end_time="10:00", activity="前往故宫并游览"),
            TimeSlot(start_time="10:30", end_time="12:00", activity="继续游览故宫"),
            TimeSlot(start_time="13:00", end_time="15:00", activity="前往鸟巢游览"),
        ],
        attractions=[
            AttractionDetail(
                id="uuid-1",
                name="北京故宫",
                image_url="https://images.unsplash.com/example-forbidden-city",
                play_duration="2-3小时",
                description="中国明清两代的皇家宫殿，世界上现存规模最大的宫殿型建筑",
                features="世界文化遗产，5A景区",
                tips="建议提前网上购票，避开周末高峰",
                latitude=39.9163,
                longitude=116.3972,
            ),
            AttractionDetail(
                id="uuid-2",
                name="国家体育场（鸟巢）",
                image_url="https://images.unsplash.com/example-birds-nest",
                play_duration="1-2小时",
                description="2008年北京奥运会主体育场",
                features="标志性建筑，可参观内部",
                tips="夜间灯光效果更佳",
                latitude=39.9928,
                longitude=116.3973,
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
                description="地铁1号线 天安门东站 -> 奥林匹克公园站",
            ),
        ],
        weather=WeatherInfo(
            date="2026-07-01",
            condition="晴",
            temperature=TemperatureRange(low=22, high=32),
            wind_speed="微风",
        ),
    )
    daily_itineraries.append(day1)

    # 第 2 天行程
    day2 = DailyItineraryDetail(
        day_index=2,
        date="2026-07-02",
        summary="长城一日游",
        schedule=[
            TimeSlot(start_time="07:00", end_time="09:00", activity="乘车前往八达岭长城"),
            TimeSlot(start_time="09:00", end_time="13:00", activity="游览八达岭长城"),
            TimeSlot(start_time="14:00", end_time="16:00", activity="返回市区，前往王府井"),
        ],
        attractions=[
            AttractionDetail(
                id="uuid-3",
                name="八达岭长城",
                image_url="",  # 无图片，用于测试 unsplash 补充逻辑
                play_duration="3-4小时",
                description="万里长城的精华段落，保存完好",
                features="世界文化遗产，5A景区",
                tips="建议穿舒适的运动鞋，携带足够的水",
                latitude=40.3545,
                longitude=116.0137,
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
            breakfast="酒店自助早餐",
            lunch="长城脚下农家菜",
            dinner="王府井小吃街美食",
        ),
        transportation=[
            TransportationPlan(
                type="大巴",
                description="德胜门乘坐877路公交车直达八达岭",
            ),
        ],
        weather=WeatherInfo(
            date="2026-07-02",
            condition="多云",
            temperature=TemperatureRange(low=20, high=30),
            wind_speed="3级",
        ),
    )
    daily_itineraries.append(day2)

    plan = TravelPlanFull(
        id=plan_id,
        destination=DestinationCity(
            name="北京",
            latitude=39.9042,
            longitude=116.4074,
        ),
        date_range=DateRange(
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
        ),
        description="北京5日游旅行计划",
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


class TestGetDayDetailContract:
    """GET /api/v1/travel-plans/{id}/day/{dayIndex} 合约测试."""

    async def test_valid_day_returns_200(self, client, plan_with_multiple_days):
        """有效的计划 ID 和 dayIndex 返回 200 OK."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1"
        )
        assert response.status_code == 200

    async def test_response_contains_day_index(self, client, plan_with_multiple_days):
        """响应包含 dayIndex 字段."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1"
        )
        data = response.json()
        assert data["dayIndex"] == 1

    async def test_response_contains_date(self, client, plan_with_multiple_days):
        """响应包含 date 字段."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1"
        )
        data = response.json()
        assert "date" in data
        assert data["date"] == "2026-07-01"

    async def test_response_contains_summary(self, client, plan_with_multiple_days):
        """响应包含 summary 字段."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1"
        )
        data = response.json()
        assert "summary" in data

    async def test_response_contains_schedule(self, client, plan_with_multiple_days):
        """响应包含 schedule 数组，每项有 startTime/endTime/activity."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1"
        )
        data = response.json()
        assert "schedule" in data
        assert isinstance(data["schedule"], list)
        assert len(data["schedule"]) > 0

        slot = data["schedule"][0]
        assert "startTime" in slot
        assert "endTime" in slot
        assert "activity" in slot

    async def test_response_contains_attractions(self, client, plan_with_multiple_days):
        """响应包含 attractions 数组."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1"
        )
        data = response.json()
        assert "attractions" in data
        assert isinstance(data["attractions"], list)
        assert len(data["attractions"]) == 2  # 第1天有2个景点

    async def test_attraction_detail_structure(self, client, plan_with_multiple_days):
        """景点详情包含 id, name, imageUrl, playDuration, description 等字段."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1"
        )
        data = response.json()
        attr = data["attractions"][0]
        assert "id" in attr
        assert "name" in attr
        assert "imageUrl" in attr
        assert "playDuration" in attr
        assert "description" in attr
        assert "features" in attr
        assert "tips" in attr
        assert "latitude" in attr
        assert "longitude" in attr

    async def test_response_contains_accommodation(self, client, plan_with_multiple_days):
        """响应包含 accommodation 对象."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1"
        )
        data = response.json()
        assert "accommodation" in data
        acc = data["accommodation"]
        assert acc is not None
        assert "hotelName" in acc
        assert "roomType" in acc
        assert "address" in acc
        assert "checkIn" in acc
        assert "checkOut" in acc
        assert "amenities" in acc

    async def test_response_contains_dining(self, client, plan_with_multiple_days):
        """响应包含 dining 对象."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1"
        )
        data = response.json()
        assert "dining" in data
        dining = data["dining"]
        assert dining is not None
        assert "breakfast" in dining
        assert "lunch" in dining
        assert "dinner" in dining

    async def test_response_contains_transportation(self, client, plan_with_multiple_days):
        """响应包含 transportation 数组."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1"
        )
        data = response.json()
        assert "transportation" in data
        assert isinstance(data["transportation"], list)
        assert len(data["transportation"]) > 0

        trans = data["transportation"][0]
        assert "type" in trans
        assert "description" in trans

    async def test_response_contains_weather(self, client, plan_with_multiple_days):
        """响应包含 weather 对象."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1"
        )
        data = response.json()
        assert "weather" in data
        weather = data["weather"]
        assert weather is not None
        assert "date" in weather
        assert "condition" in weather
        assert "temperature" in weather
        assert "windSpeed" in weather
        assert "low" in weather["temperature"]
        assert "high" in weather["temperature"]

    async def test_day_index_2_returns_different_data(self, client, plan_with_multiple_days):
        """请求第2天返回不同于第1天的数据."""
        response1 = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1"
        )
        response2 = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/2"
        )
        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()
        assert data1["dayIndex"] != data2["dayIndex"]
        assert data1["summary"] != data2["summary"]

    async def test_nonexistent_plan_returns_404(self, client):
        """不存在的计划 ID 返回 404."""
        response = await client.get(
            "/api/v1/travel-plans/nonexistent-id/day/1"
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    async def test_day_index_out_of_range_returns_404(self, client, plan_with_multiple_days):
        """dayIndex 超出范围返回 404."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/10"
        )
        assert response.status_code == 404

    async def test_day_index_zero_returns_400(self, client, plan_with_multiple_days):
        """dayIndex 为 0 返回 400（dayIndex 从 1 开始）."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/0"
        )
        assert response.status_code == 400

    async def test_day_index_negative_returns_422(self, client, plan_with_multiple_days):
        """dayIndex 为负数返回 422（路径参数验证）."""
        response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/-1"
        )
        assert response.status_code == 422
