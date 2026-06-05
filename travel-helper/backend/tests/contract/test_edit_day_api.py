"""PUT /api/v1/travel-plans/{id}/day/{dayIndex} API 合约测试.

验证端点更新当日行程数据的行为符合 contracts/api-contract.md 定义的格式。
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

    plan_id = "test-edit-day-plan-001"

    budget = BudgetBreakdown(
        attraction_tickets=3390,
        hotel_accommodation=3600,
        dining_transport=2190,
        dining_food=900,
        total=10080,
    )

    daily_itineraries = []

    # 第 1 天 — 3 个景点
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
                image_url="https://images.unsplash.com/forbidden-city",
                play_duration="2-3小时",
                description="中国明清两代的皇家宫殿",
                features="世界文化遗产",
                tips="建议提前网上购票",
                latitude=39.9163,
                longitude=116.3972,
            ),
            AttractionDetail(
                id="uuid-2",
                name="国家体育场（鸟巢）",
                image_url="https://images.unsplash.com/birds-nest",
                play_duration="1-2小时",
                description="2008年北京奥运会主体育场",
                features="标志性建筑",
                tips="夜间灯光效果更佳",
                latitude=39.9928,
                longitude=116.3973,
            ),
            AttractionDetail(
                id="uuid-3",
                name="水立方",
                image_url="",
                play_duration="1小时",
                description="国家游泳中心",
                features="奥运场馆",
                tips="",
                latitude=39.9930,
                longitude=116.3975,
            ),
        ],
        accommodation=AccommodationPlan(
            hotel_name="北京万豪酒店",
            room_type="豪华标准间",
            address="北京市朝阳区xxx路xxx号",
            check_in="2026-07-01",
            check_out="2026-07-03",
            amenities="免费WiFi、停车位",
            latitude=39.9200,
            longitude=116.4100,
        ),
        dining=DiningPlan(
            breakfast="北京传统早餐",
            lunch="北京烤鸭",
            dinner="北京炸酱面",
        ),
        transportation=[
            TransportationPlan(type="地铁", description="地铁1号线"),
        ],
        weather=WeatherInfo(
            date="2026-07-01",
            condition="晴",
            temperature=TemperatureRange(low=22, high=32),
            wind_speed="微风",
        ),
    )
    daily_itineraries.append(day1)

    # 第 2 天 — 2 个景点
    day2 = DailyItineraryDetail(
        day_index=2,
        date="2026-07-02",
        summary="颐和园 - 圆明园",
        schedule=[
            TimeSlot(start_time="08:00", end_time="12:00", activity="游览颐和园"),
            TimeSlot(start_time="13:00", end_time="16:00", activity="游览圆明园"),
        ],
        attractions=[
            AttractionDetail(
                id="uuid-4",
                name="颐和园",
                image_url="",
                play_duration="3-4小时",
                description="中国古典园林之首",
                features="世界文化遗产",
                tips="",
                latitude=39.9985,
                longitude=116.2745,
            ),
            AttractionDetail(
                id="uuid-5",
                name="圆明园",
                image_url="",
                play_duration="2-3小时",
                description="万园之园",
                features="历史遗迹",
                tips="",
                latitude=40.0083,
                longitude=116.2983,
            ),
        ],
        accommodation=None,
        dining=DiningPlan(
            breakfast="酒店自助早餐",
            lunch="园区附近简餐",
            dinner="返回市区用餐",
        ),
        transportation=[
            TransportationPlan(type="地铁", description="地铁4号线"),
        ],
        weather=WeatherInfo(
            date="2026-07-02",
            condition="晴",
            temperature=TemperatureRange(low=21, high=31),
            wind_speed="微风",
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


class TestEditDayContract:
    """PUT /api/v1/travel-plans/{id}/day/{dayIndex} 合约测试."""

    async def test_valid_update_returns_200(self, client, plan_with_multiple_days):
        """有效的更新请求返回 200 OK."""
        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "12:00", "activity": "游览故宫"},
                {"startTime": "13:00", "endTime": "15:00", "activity": "游览鸟巢"},
            ],
            "attractions": [
                {
                    "id": "uuid-1",
                    "name": "北京故宫",
                    "imageUrl": "https://images.unsplash.com/forbidden-city",
                    "playDuration": "2-3小时",
                    "description": "中国明清两代的皇家宫殿",
                    "features": "世界文化遗产",
                    "tips": "建议提前网上购票",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                },
                {
                    "id": "uuid-2",
                    "name": "国家体育场（鸟巢）",
                    "imageUrl": "https://images.unsplash.com/birds-nest",
                    "playDuration": "1-2小时",
                    "description": "2008年北京奥运会主体育场",
                    "features": "标志性建筑",
                    "tips": "夜间灯光效果更佳",
                    "latitude": 39.9928,
                    "longitude": 116.3973,
                },
            ],
            "accommodation": {
                "hotelName": "北京万豪酒店",
                "roomType": "豪华标准间",
                "address": "北京市朝阳区xxx路xxx号",
                "checkIn": "2026-07-01",
                "checkOut": "2026-07-03",
                "amenities": "免费WiFi、停车位",
                "latitude": 39.9200,
                "longitude": 116.4100,
            },
            "dining": {
                "breakfast": "北京传统早餐",
                "lunch": "北京烤鸭",
                "dinner": "北京炸酱面",
            },
            "transportation": [
                {"type": "地铁", "description": "地铁1号线"},
            ],
        }

        response = await client.put(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1",
            json=payload,
        )
        assert response.status_code == 200

    async def test_response_has_required_fields(self, client, plan_with_multiple_days):
        """响应包含 message, dayIndex, updatedAt 字段."""
        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "12:00", "activity": "游览故宫"},
            ],
            "attractions": [
                {
                    "id": "uuid-1",
                    "name": "北京故宫",
                    "imageUrl": "",
                    "playDuration": "2小时",
                    "description": "",
                    "features": "",
                    "tips": "",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                },
            ],
        }

        response = await client.put(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1",
            json=payload,
        )
        data = response.json()

        assert "message" in data
        assert "dayIndex" in data
        assert "updatedAt" in data

    async def test_response_message_is_success(self, client, plan_with_multiple_days):
        """响应 message 字段为成功消息."""
        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "12:00", "activity": "游览"},
            ],
            "attractions": [
                {
                    "id": "uuid-1",
                    "name": "北京故宫",
                    "imageUrl": "",
                    "playDuration": "2小时",
                    "description": "",
                    "features": "",
                    "tips": "",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                },
            ],
        }

        response = await client.put(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1",
            json=payload,
        )
        data = response.json()
        assert data["message"] == "Day itinerary updated successfully"

    async def test_response_day_index_matches_path(self, client, plan_with_multiple_days):
        """响应 dayIndex 与路径参数一致."""
        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "12:00", "activity": "游览"},
            ],
            "attractions": [
                {
                    "id": "uuid-1",
                    "name": "北京故宫",
                    "imageUrl": "",
                    "playDuration": "2小时",
                    "description": "",
                    "features": "",
                    "tips": "",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                },
            ],
        }

        response = await client.put(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/2",
            json=payload,
        )
        data = response.json()
        assert data["dayIndex"] == 2

    async def test_response_updated_at_is_iso_format(self, client, plan_with_multiple_days):
        """响应 updatedAt 为 ISO 8601 格式时间戳."""
        import re

        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "12:00", "activity": "游览"},
            ],
            "attractions": [
                {
                    "id": "uuid-1",
                    "name": "北京故宫",
                    "imageUrl": "",
                    "playDuration": "2小时",
                    "description": "",
                    "features": "",
                    "tips": "",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                },
            ],
        }

        response = await client.put(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1",
            json=payload,
        )
        data = response.json()
        assert "updatedAt" in data
        # 检查 ISO 8601 格式
        iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
        assert re.match(iso_pattern, data["updatedAt"]) is not None

    async def test_update_with_empty_attractions_returns_400(self, client, plan_with_multiple_days):
        """请求 attractions 为空数组时返回 400."""
        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "12:00", "activity": "自由活动"},
            ],
            "attractions": [],  # 空景点列表
        }

        response = await client.put(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1",
            json=payload,
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "至少保留 1 个景点" in data["detail"]

    async def test_update_nonexistent_plan_returns_404(self, client):
        """不存在的计划 ID 返回 404."""
        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "12:00", "activity": "游览"},
            ],
            "attractions": [
                {
                    "id": "uuid-1",
                    "name": "北京故宫",
                    "imageUrl": "",
                    "playDuration": "2小时",
                    "description": "",
                    "features": "",
                    "tips": "",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                },
            ],
        }

        response = await client.put(
            "/api/v1/travel-plans/nonexistent-id/day/1",
            json=payload,
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    async def test_update_nonexistent_day_returns_404(self, client, plan_with_multiple_days):
        """不存在的 dayIndex 返回 404."""
        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "12:00", "activity": "游览"},
            ],
            "attractions": [
                {
                    "id": "uuid-1",
                    "name": "北京故宫",
                    "imageUrl": "",
                    "playDuration": "2小时",
                    "description": "",
                    "features": "",
                    "tips": "",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                },
            ],
        }

        response = await client.put(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/10",
            json=payload,
        )
        assert response.status_code == 404

    async def test_update_day_index_zero_returns_400(self, client, plan_with_multiple_days):
        """dayIndex 为 0 返回 400."""
        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "12:00", "activity": "游览"},
            ],
            "attractions": [
                {
                    "id": "uuid-1",
                    "name": "北京故宫",
                    "imageUrl": "",
                    "playDuration": "2小时",
                    "description": "",
                    "features": "",
                    "tips": "",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                },
            ],
        }

        response = await client.put(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/0",
            json=payload,
        )
        assert response.status_code == 400

    async def test_update_persists_changes(self, client, plan_with_multiple_days):
        """更新后，GET 端点应返回更新后的数据."""
        # 先更新第 1 天
        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "12:00", "activity": "更新后的游览故宫"},
            ],
            "attractions": [
                {
                    "id": "uuid-1",
                    "name": "北京故宫（已编辑）",
                    "imageUrl": "",
                    "playDuration": "2小时",
                    "description": "更新后的描述",
                    "features": "",
                    "tips": "",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                },
            ],
        }

        put_response = await client.put(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1",
            json=payload,
        )
        assert put_response.status_code == 200

        # 再 GET 验证更新
        get_response = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1",
        )
        assert get_response.status_code == 200
        data = get_response.json()
        assert len(data["attractions"]) == 1
        assert data["attractions"][0]["name"] == "北京故宫（已编辑）"
        assert data["schedule"][0]["activity"] == "更新后的游览故宫"

    async def test_update_partial_payload(self, client, plan_with_multiple_days):
        """部分载荷（仅 attractions 和 schedule）也能成功更新."""
        payload = {
            "schedule": [
                {"startTime": "10:00", "endTime": "15:00", "activity": "半日游"},
            ],
            "attractions": [
                {
                    "id": "uuid-4",
                    "name": "颐和园",
                    "imageUrl": "",
                    "playDuration": "2小时",
                    "description": "更新后的描述",
                    "features": "",
                    "tips": "",
                    "latitude": 39.9985,
                    "longitude": 116.2745,
                },
            ],
        }

        response = await client.put(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/2",
            json=payload,
        )
        assert response.status_code == 200

    async def test_update_does_not_affect_other_days(self, client, plan_with_multiple_days):
        """更新第 1 天不应影响第 2 天的数据."""
        # 记录第 2 天原始数据
        get_day2_before = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/2",
        )
        day2_before = get_day2_before.json()

        # 更新第 1 天
        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "12:00", "activity": "游览"},
            ],
            "attractions": [
                {
                    "id": "uuid-1",
                    "name": "北京故宫",
                    "imageUrl": "",
                    "playDuration": "2小时",
                    "description": "",
                    "features": "",
                    "tips": "",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                },
            ],
        }

        await client.put(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/1",
            json=payload,
        )

        # 验证第 2 天未改变
        get_day2_after = await client.get(
            f"/api/v1/travel-plans/{plan_with_multiple_days}/day/2",
        )
        day2_after = get_day2_after.json()

        assert day2_before["summary"] == day2_after["summary"]
        assert len(day2_before["attractions"]) == len(day2_after["attractions"])
